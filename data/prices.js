/**
 * prices.js — Live price data loaded as a <script> tag
 * Works on: local file://, GitHub Pages, any static host
 * Auto-updated by GitHub Actions scraper (writes this file daily)
 * Fallback: hardcoded Mar 2026 KRAMA/KisanDeals verified data
 */
window.CHILLI_PRICES = {
  last_updated: "2026-03-27",
  fetch_status: "seed_data",
  markets: [
    {
      market: "Sindhanur APMC",
      district: "Raichur",
      variety: "Dry Chillies (Hybrid — 2043/5531 proxy)",
      min_price: 7300,
      modal_price: 13300,
      max_price: 13300,
      date: "2026-03-25",
      unit: "INR per Quintal",
      source: "KRAMA Karnataka + KisanDeals"
    },
    {
      market: "Hubli Amaragol APMC",
      district: "Dharwad",
      variety: "Dry Chillies (Byadgi Premium + Mixed)",
      min_price: 2400,
      modal_price: 27501,
      max_price: 48399,
      date: "2026-03-23",
      unit: "INR per Quintal",
      source: "KisanDeals"
    },
    {
      market: "Mangalore APMC",
      district: "Dakshina Kannada",
      variety: "Dry Chillies",
      min_price: 19000,
      modal_price: 20000,
      max_price: 25000,
      date: "2026-03-24",
      unit: "INR per Quintal",
      source: "KisanDeals"
    }
  ],
  summary: {
    hybrid_modal_today: 13300,
    byadgi_modal_today: 27501,
    season_peak_2026: 39207,
    season_peak_date: "2026-02-24",
    trend: "declining",
    trend_note: "Late-harvest period. Peak was Feb 2026 (₹39,207). Recovery expected Oct–Nov 2026."
  },
  variety_estimates: {
    syngenta_2043: {
      estimated_modal: 13300,
      range_low: 7300,
      range_high: 20000,
      note: "Tracks Sindhanur APMC hybrid price (Mar 2026)"
    },
    syngenta_5531: {
      estimated_modal: 14200,
      range_low: 8000,
      range_high: 22000,
      note: "5-10% premium over 2043 (masala+colour dual appeal)"
    }
  }
};
