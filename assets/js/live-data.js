/**
 * live-data.js — Unified live price loader
 *
 * Strategy (in order):
 *  1. Try Agmarknet public API directly from browser (truly live)
 *  2. Try loading data/live-prices.json (works on GitHub Pages server)
 *  3. Use window.CHILLI_PRICES from data/prices.js (always works, loaded as <script>)
 *
 * Call:  loadLiveData().then(d => { ... })
 * Returns a normalised price object every time — never fails.
 */

// ─── Agmarknet public API (no API key needed for this endpoint) ──────────
const AGMARK_URL =
  "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070" +
  "?api-key=579b464db66ec23bdd0000016cc8a3c7c9c4408e8e8048e2e13f6ab0" +
  "&format=json&limit=30" +
  "&filters[State]=Karnataka" +
  "&filters[Commodity]=Dry+Chillies";

// Known Ballari-area target markets
const TARGET_MARKETS = ["sindhanur","hubli","byadgi","ballari","bellary","raichur"];

// ─── Normalise from Agmarknet record ────────────────────────────────────
function normaliseAgmark(records) {
  const markets = [];
  records.forEach(rec => {
    const mkt  = (rec["Market"]       || "").trim();
    const dist = (rec["District"]     || "").trim();
    const vty  = (rec["Variety"]      || "Dry Chillies").trim();
    const minP = parseInt(rec["Min Price"]   || 0, 10);
    const modP = parseInt(rec["Modal Price"] || 0, 10);
    const maxP = parseInt(rec["Max Price"]   || 0, 10);
    const dt   = rec["Arrival Date"] || new Date().toISOString().slice(0,10);
    if (modP > 1000) markets.push({ market: mkt, district: dist, variety: vty,
      min_price: minP, modal_price: modP, max_price: maxP,
      date: dt, unit: "INR per Quintal", source: "Agmarknet/live" });
  });
  return markets;
}

function buildSummary(markets) {
  const hyb = markets.filter(m =>
    TARGET_MARKETS.some(k => m.market.toLowerCase().includes(k)));
  const prem = markets.filter(m =>
    ["hubli","byadgi","amaragol"].some(k => m.market.toLowerCase().includes(k)));

  const hybModal = hyb.length
    ? Math.round(hyb.reduce((s,m)=>s+m.modal_price,0)/hyb.length)
    : (window.CHILLI_PRICES?.summary?.hybrid_modal_today || 13300);

  const premModal = prem.length
    ? Math.round(prem.reduce((s,m)=>s+m.modal_price,0)/prem.length)
    : (window.CHILLI_PRICES?.summary?.byadgi_modal_today || 27501);

  let trend = "stable", trendNote = "Average market conditions. Monitor weekly.";
  if      (hybModal > 18000) { trend = "rising";   trendNote = "Above-average prices — good time to sell."; }
  else if (hybModal > 14000) { trend = "stable";   trendNote = "Average market. Monitor weekly before selling."; }
  else if (hybModal > 10000) { trend = "declining"; trendNote = "Below-average. Sell only best quality lots now."; }
  else                       { trend = "very_low"; trendNote = "Prices near trough. Consider cold storage."; }

  return {
    hybrid_modal_today: hybModal,
    byadgi_modal_today: premModal,
    trend, trend_note: trendNote,
    season_peak_2026: window.CHILLI_PRICES?.summary?.season_peak_2026 || 39207,
    season_peak_date: window.CHILLI_PRICES?.summary?.season_peak_date || "2026-02-24"
  };
}

function buildVarietyEstimates(hybModal) {
  return {
    syngenta_2043: {
      estimated_modal: hybModal,
      range_low: Math.round(hybModal * 0.65),
      range_high: Math.round(hybModal * 1.45),
      note: "Tracks hybrid price at Sindhanur/Raichur APMC"
    },
    syngenta_5531: {
      estimated_modal: Math.round(hybModal * 1.07),
      range_low: Math.round(hybModal * 0.70),
      range_high: Math.round(hybModal * 1.55),
      note: "5–10% premium over 2043 (dual masala + colour appeal)"
    }
  };
}

// ─── Layer 1: Agmarknet live API ─────────────────────────────────────────
async function tryAgmarknet() {
  try {
    const res = await fetch(AGMARK_URL, { signal: AbortSignal.timeout(8000) });
    if (!res.ok) throw new Error("HTTP " + res.status);
    const json = await res.json();
    const records = json.records || [];
    if (!records.length) throw new Error("No records");
    const markets = normaliseAgmark(records);
    if (!markets.length) throw new Error("No valid markets");
    const summary = buildSummary(markets);
    return {
      last_updated: new Date().toISOString().slice(0,10),
      fetch_status: "live_agmarknet",
      source_label: "Live — Agmarknet API",
      markets,
      summary,
      variety_estimates: buildVarietyEstimates(summary.hybrid_modal_today)
    };
  } catch (e) {
    console.warn("[prices] Agmarknet failed:", e.message);
    return null;
  }
}

// ─── Layer 2: data/live-prices.json (GitHub Pages server) ───────────────
async function tryJsonFile() {
  try {
    const res = await fetch("data/live-prices.json?v=" + Date.now(),
      { signal: AbortSignal.timeout(5000) });
    if (!res.ok) throw new Error("HTTP " + res.status);
    const json = await res.json();
    if (!json.markets?.length) throw new Error("Empty");
    json.source_label = "GitHub Actions cache";
    return json;
  } catch (e) {
    console.warn("[prices] JSON file fetch failed:", e.message);
    return null;
  }
}

// ─── Layer 3: Embedded window.CHILLI_PRICES (always available) ──────────
function useEmbedded() {
  const d = window.CHILLI_PRICES || {};
  return {
    last_updated: d.last_updated || "2026-03-27",
    fetch_status: "embedded_seed",
    source_label: "Embedded seed data (Mar 2026)",
    markets: d.markets || [],
    summary: d.summary || { hybrid_modal_today: 13300, byadgi_modal_today: 27501,
      trend: "declining", trend_note: "Late harvest period. Mar 2026 data." },
    variety_estimates: d.variety_estimates || buildVarietyEstimates(13300)
  };
}

// ─── Main loader ─────────────────────────────────────────────────────────
async function loadLiveData() {
  const live = await tryAgmarknet();
  if (live) return live;

  const cached = await tryJsonFile();
  if (cached) return cached;

  return useEmbedded();
}

// ─── Render a live ticker bar ─────────────────────────────────────────────
function renderTicker(data) {
  const ve   = data.variety_estimates || {};
  const m    = data.markets || [];
  const v2   = ve.syngenta_2043?.estimated_modal;
  const v5   = ve.syngenta_5531?.estimated_modal;
  const sindh = m.find(x => x.market.toLowerCase().includes("sindhanur"))?.modal_price;
  const hubli = m.find(x => x.market.toLowerCase().includes("hubli"))?.modal_price;
  const fmt  = n => n ? "₹" + Number(n).toLocaleString("en-IN") + "/Q" : "—";
  const statusIcon = data.fetch_status === "live_agmarknet" ? "🟢" :
                     data.fetch_status === "embedded_seed"  ? "🟡" : "🔵";

  const ids = {
    "t-sindhanur": fmt(sindh), "t-s": fmt(sindh),
    "t-hubli":     fmt(hubli), "t-h": fmt(hubli),
    "t-2043":      fmt(v2),    "t-2": fmt(v2),
    "t-5531":      fmt(v5),    "t-5": fmt(v5)
  };
  Object.entries(ids).forEach(([id, val]) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  });

  const updEl = document.getElementById("t-updated") || document.getElementById("t-u");
  if (updEl) updEl.textContent = `${statusIcon} ${data.source_label} · ${data.last_updated}`;

  return { sindh, hubli, v2, v5 };
}
