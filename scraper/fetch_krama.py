"""
fetch_krama.py — Daily price scraper for Karnataka chilli APMC data
Fetches from:
  1. KRAMA Karnataka portal (HTML scraping)
  2. Agmarknet / data.gov.in API (free, no key needed for public data)
Saves to: ../data/live-prices.json

Run by GitHub Actions every day at 8:30 AM IST (3:00 AM UTC)
"""

import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

TODAY = datetime.now().strftime("%d/%m/%Y")
TODAY_ISO = datetime.now().strftime("%Y-%m-%d")

# ─────────────────────────────────────────────────────────────────────────────
# KRAMA URL BUILDER
# CommCode=132 = Dry Chillies, VarCode=1 = Byadgi variety
# ─────────────────────────────────────────────────────────────────────────────
KRAMA_BASE = "https://krama.karnataka.gov.in/MainPage/DailyMrktPriceRep2"
KRAMA_PARAMS_BYADGI = {
    "Rep": "Com",
    "CommCode": "132",
    "VarCode": "1",
    "Date": TODAY,
    "CommName": "Dry Chillies",
    "VarName": "Byadgi",
}

# Sindhanur APMC (hybrid chilli — closest proxy for 2043/5531)
KRAMA_PARAMS_SINDHANUR = {
    "Rep": "Mkt",
    "MktCode": "105",   # Sindhanur APMC market code
    "CommCode": "132",
    "Date": TODAY,
}

# ─────────────────────────────────────────────────────────────────────────────
# AGMARKNET DATA.GOV.IN — Free daily APMC prices (Karnataka, Dry Chillies)
# Resource ID: 9ef84268-d588-465a-a308-a864a43d0070
# ─────────────────────────────────────────────────────────────────────────────
AGMARK_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
AGMARK_PARAMS = {
    "api-key": "579b464db66ec23bdd0000016cc8a3c7c9c4408e8e8048e2e13f6ab0",  # public demo key
    "format": "json",
    "limit": "50",
    "filters[State]": "Karnataka",
    "filters[Commodity]": "Dry Chillies",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ChilliFarmerBot/1.0; +https://github.com)",
    "Accept": "text/html,application/xhtml+xml,application/json",
    "Accept-Language": "en-US,en;q=0.9",
}

TARGET_MARKETS = {
    "sindhanur": ["sindhanur", "sindhanur apmc"],
    "hubli": ["hubli", "hubli amaragol", "hubli (amaragol)"],
    "byadgi": ["byadgi", "byadgi apmc"],
    "bellary": ["bellary", "ballari", "ballari apmc", "bellary apmc"],
    "raichur": ["raichur", "raichur apmc"],
}


def try_krama_byadgi():
    """Scrape KRAMA portal for Byadgi variety daily market prices."""
    results = []
    for attempt in range(3):
        try:
            r = requests.get(KRAMA_BASE, params=KRAMA_PARAMS_BYADGI,
                             headers=HEADERS, timeout=15)
            if r.status_code != 200:
                log.warning(f"KRAMA returned {r.status_code}")
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            tables = soup.find_all("table")

            for table in tables:
                rows = table.find_all("tr")
                for row in rows[1:]:
                    cols = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
                    if len(cols) >= 4:
                        # Try to parse: Market | Min | Modal | Max
                        try:
                            market_name = cols[0].strip()
                            min_p = int(cols[-3].replace(",", "").replace("₹", "").strip())
                            modal_p = int(cols[-2].replace(",", "").replace("₹", "").strip())
                            max_p = int(cols[-1].replace(",", "").replace("₹", "").strip())
                            if modal_p > 1000:
                                results.append({
                                    "market": market_name,
                                    "district": "",
                                    "variety": "Byadgi Dry Chilli",
                                    "min_price": min_p,
                                    "modal_price": modal_p,
                                    "max_price": max_p,
                                    "date": TODAY_ISO,
                                    "unit": "INR per Quintal",
                                    "source": "KRAMA"
                                })
                        except (ValueError, IndexError):
                            continue

            if results:
                log.info(f"KRAMA Byadgi: fetched {len(results)} markets")
                return results

        except Exception as e:
            log.warning(f"KRAMA attempt {attempt+1} failed: {e}")

    log.warning("KRAMA fetch failed — will use fallback data")
    return []


def try_agmarknet():
    """Fetch Karnataka dry chilli prices from Agmarknet (data.gov.in)."""
    results = []
    try:
        r = requests.get(AGMARK_URL, params=AGMARK_PARAMS,
                         headers=HEADERS, timeout=20)
        if r.status_code != 200:
            log.warning(f"Agmarknet returned {r.status_code}")
            return []

        data = r.json()
        records = data.get("records", [])

        for rec in records:
            market = rec.get("Market", "").strip()
            district = rec.get("District", "").strip()
            variety = rec.get("Variety", "").strip()
            try:
                min_p = int(float(rec.get("Min Price", 0)))
                modal_p = int(float(rec.get("Modal Price", 0)))
                max_p = int(float(rec.get("Max Price", 0)))
                arr_date = rec.get("Arrival Date", TODAY_ISO)
            except (ValueError, TypeError):
                continue

            if modal_p > 1000:
                results.append({
                    "market": market,
                    "district": district,
                    "variety": variety if variety else "Dry Chillies",
                    "min_price": min_p,
                    "modal_price": modal_p,
                    "max_price": max_p,
                    "date": arr_date,
                    "unit": "INR per Quintal",
                    "source": "Agmarknet"
                })

        if results:
            log.info(f"Agmarknet: fetched {len(results)} records")
        return results

    except Exception as e:
        log.warning(f"Agmarknet fetch failed: {e}")
        return []


def get_fallback_data():
    """Return last known good data if all fetches fail."""
    log.warning("Using hardcoded fallback data from Mar 2026")
    return [
        {
            "market": "Sindhanur APMC",
            "district": "Raichur",
            "variety": "Dry Chillies (Hybrid)",
            "min_price": 7300,
            "modal_price": 13300,
            "max_price": 13300,
            "date": "2026-03-25",
            "unit": "INR per Quintal",
            "source": "fallback"
        },
        {
            "market": "Hubli Amaragol APMC",
            "district": "Dharwad",
            "variety": "Dry Chillies (Byadgi)",
            "min_price": 2400,
            "modal_price": 27501,
            "max_price": 48399,
            "date": "2026-03-23",
            "unit": "INR per Quintal",
            "source": "fallback"
        }
    ]


def compute_summary(markets):
    """Compute summary statistics from market data."""
    hybrid_markets = [m for m in markets
                      if any(k in m["market"].lower()
                             for k in ["sindhanur", "raichur", "bellary", "ballari"])]
    premium_markets = [m for m in markets
                       if any(k in m["market"].lower()
                              for k in ["hubli", "byadgi", "amaragol"])]

    hybrid_modal = (
        int(sum(m["modal_price"] for m in hybrid_markets) / len(hybrid_markets))
        if hybrid_markets else 13300
    )
    byadgi_modal = (
        int(sum(m["modal_price"] for m in premium_markets) / len(premium_markets))
        if premium_markets else 27501
    )

    # Trend detection: compare to 30-day moving estimate
    if hybrid_modal > 18000:
        trend, trend_note = "rising", "Above-average prices — good time to sell 2043/5531."
    elif hybrid_modal > 14000:
        trend, trend_note = "stable", "Average market conditions. Monitor weekly."
    elif hybrid_modal > 10000:
        trend, trend_note = "declining", "Below-average. Hold stock if possible, or sell best lots now."
    else:
        trend, trend_note = "very_low", "Prices near trough. Consider cold storage and wait."

    return {
        "hybrid_modal_today": hybrid_modal,
        "byadgi_modal_today": byadgi_modal,
        "trend": trend,
        "trend_note": trend_note
    }


def estimate_variety_prices(hybrid_modal):
    """Estimate 2043 and 5531 prices from hybrid modal."""
    return {
        "syngenta_2043": {
            "estimated_modal": hybrid_modal,
            "range_low": int(hybrid_modal * 0.65),
            "range_high": int(hybrid_modal * 1.45),
            "note": "Tracks Sindhanur APMC generic hybrid price. Higher ASTA colour."
        },
        "syngenta_5531": {
            "estimated_modal": int(hybrid_modal * 1.07),
            "range_low": int(hybrid_modal * 0.70),
            "range_high": int(hybrid_modal * 1.55),
            "note": "5-10% premium over 2043 due to dual colour+pungency appeal."
        }
    }


def main():
    log.info(f"=== Chilli Price Fetch — {TODAY_ISO} ===")

    # Try sources in priority order
    markets = try_krama_byadgi()
    if not markets:
        markets = try_agmarknet()
    if not markets:
        markets = get_fallback_data()
        fetch_status = "fallback"
    else:
        fetch_status = "live"

    summary = compute_summary(markets)
    variety_est = estimate_variety_prices(summary["hybrid_modal_today"])

    output = {
        "last_updated": TODAY_ISO,
        "fetch_status": fetch_status,
        "note": "Auto-updated daily by GitHub Actions at 8:30 AM IST.",
        "markets": markets,
        "summary": summary,
        "variety_estimates": variety_est
    }

    out_path = "../data/live-prices.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    log.info(f"Saved {len(markets)} market records → {out_path}")
    log.info(f"Hybrid modal: ₹{summary['hybrid_modal_today']:,} | Status: {fetch_status}")


if __name__ == "__main__":
    main()


def write_prices_js(output):
    """Also write data/prices.js so it works without a fetch/server."""
    import json
    js_path = "../data/prices.js"
    content = (
        "// Auto-updated by GitHub Actions. DO NOT EDIT manually.\n"
        "// Last updated: " + output["last_updated"] + "\n"
        "window.CHILLI_PRICES = " + json.dumps(output, ensure_ascii=False, indent=2) + ";\n"
    )
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(content)
    log.info(f"Saved → {js_path}")


# Monkey-patch main to also write prices.js
_original_main = main
def main():
    _original_main()
    # Re-read what was written and also create prices.js
    import json
    with open("../data/live-prices.json", encoding="utf-8") as f:
        output = json.load(f)
    write_prices_js(output)

if __name__ == "__main__":
    main()
