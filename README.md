# 🌶 ChilliFarm Ballari - Chilli Farmer Dashboard

A free, open-source website for **chilli farmers in Ballari (Bellary), Karnataka**, India.  
Built for **Syngenta 2043 and 5531** hybrid variety growers.

> *Made with ❤️ for my father, a chilli farmer in Ballari.*

---

## 📱 What This Site Does

| Page | What It Shows |
|---|---|
| **Dashboard** (`index.html`) | Live APMC prices, market trend, quick links |
| **Price Charts** (`charts.html`) | 5 interactive charts - every 3 months from 2021 to 2026 |
| **Profit Calculator** (`calculator.html`) | Enter your farm size, costs, yield → instant profit/loss |

### Live Price Data (Auto-Updated Daily)
- Fetched every day from **KRAMA Karnataka government portal** and **Agmarknet (data.gov.in)**
- Saved to `data/live-prices.json`
- Updated by **GitHub Actions** at 8:30 AM IST and 3:30 PM IST
- No hosting costs - all free with GitHub Pages + Actions

---

## 📁 Project Structure

```
chilli-farm/
├── index.html                    # Main dashboard with live prices
├── charts.html                   # 5-year quarterly price charts
├── calculator.html               # Profit calculator
│
├── data/
│   └── live-prices.json          # ← Auto-updated daily by GitHub Actions
│
├── assets/
│   ├── css/
│   │   └── style.css             # Shared styles for all pages
│   └── js/
│       └── chart-data.js         # Historical quarterly price data (2021–2026)
│
├── scraper/
│   └── fetch_krama.py            # Python scraper (runs in GitHub Actions)
│
├── .github/
│   └── workflows/
│       └── fetch-prices.yml      # GitHub Actions daily automation
│
└── README.md                     # This file
```

---

## 📊 Price Data Sources

| Source | What it provides | How used |
|---|---|---|
| [KRAMA Karnataka](https://krama.karnataka.gov.in) | Daily APMC prices for Karnataka | Primary scrape target |
| [Agmarknet / data.gov.in](https://agmarknet.gov.in) | National APMC prices API | Backup data source |
| SpiceExtra Karnataka Reports | Verified Feb 2023 & Feb 2024 prices | Historical anchors |
| KisanDeals | Live APMC price tracker | Trough data (Aug 2025) |
| PJTAU Vanakalam Forecast | Academic ARIMA price model | 2026–27 prediction |

### Key Verified Data Points (used in charts)
| Quarter | 2043 Price | 5531 Price | Source |
|---|---|---|---|
| Q1 2023 (Jan–Mar) | ~₹18,000 | **₹22,000** ⭐ | SpiceExtra Feb 2023 |
| Q1 2024 (Jan–Mar) | ~₹13,500 | **₹15,000** ⭐ | SpiceExtra Feb 2024 |
| Q3 2025 (Jul–Sep) | **₹7,000** ⭐ | **₹7,500** ⭐ | KisanDeals trough |
| Q1 2026 (Mar 27) | **₹13,300** ⭐ | ~₹14,000 | KRAMA Sindhanur APMC |

---

## 🔧 How the Live Price Scraper Works

The file `.github/workflows/fetch-prices.yml` tells GitHub to automatically run the Python script `scraper/fetch_krama.py` every day.

**What it does:**
1. Runs at 8:30 AM IST and 3:30 PM IST every day
2. Tries to fetch prices from KRAMA Karnataka portal (HTML scraping)
3. If KRAMA fails, tries Agmarknet API (free)
4. If both fail, keeps last known good data
5. Saves result to `data/live-prices.json`
6. Commits and pushes the updated file to GitHub
7. Your website automatically shows the new prices

**No cost** - GitHub gives 2,000 free Actions minutes per month. This scraper uses about 10 minutes per month.

---

## 📈 Price Predictions for 2026–27

Based on APMC data analysis:

| Variety | Bear Case (25%) | **Base Case (55%)** | Bull Case (20%) |
|---|---|---|---|
| **Syngenta 2043** | ₹11,000–14,000 | **₹16,000–22,000** | ₹24,000–32,000 |
| **Syngenta 5531** | ₹12,000–15,000 | **₹17,000–24,000** | ₹26,000–34,000 |

**Best time to sell: January 2027** (Q1 always peaks historically)

---

## 🛠️ Customizing for Your Farm

To update the default values in the profit calculator, edit `calculator.html` and find the `costData` JavaScript object. Change the `val:` numbers to match your actual costs.

To update the historical price data, edit `assets/js/chart-data.js` and update the `p2043` and `p5531` arrays.

---

## 📞 Useful Contacts for Ballari Farmers

- **KRAMA Portal**: [krama.karnataka.gov.in](https://krama.karnataka.gov.in)
- **Krishi Vigyan Kendra Ballari**: +91-8394-220350
- **Karnataka Horticulture Department**: [horticulture.kar.nic.in](http://horticulture.kar.nic.in)
- **PMFBY Crop Insurance**: [pmfby.gov.in](https://pmfby.gov.in)
- **PM-KISAN**: [pmkisan.gov.in](https://pmkisan.gov.in)
- **PMKSY Drip Irrigation Subsidy**: Apply at local agriculture department

---

## ⚠️ Disclaimer

This website is for **planning and education purposes only**. Actual APMC prices may differ. Always verify prices on the official KRAMA portal before making selling decisions. The profit predictions are based on historical data and market analysis - they are not guaranteed.

---

## 📜 License

Free to use, modify, and share. No rights reserved. Made for farmers.

---

*Built in March 2026. Data sourced from Karnataka government APMC portals and agricultural research institutions.*
