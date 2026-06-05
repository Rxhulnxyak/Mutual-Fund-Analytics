# Mutual Fund Analytics Dashboard

> **Internship Capstone Project** — End-to-end mutual fund data pipeline, analysis, and interactive dashboard.

---

## 📁 Project Structure

```
mutual_fund_analytics/
├── data/
│   ├── raw/              # 10 original CSV datasets + live NAV CSVs
│   └── processed/        # Cleaned & feature-engineered data
├── notebooks/            # Jupyter EDA notebooks
├── sql/                  # SQL queries & schema definitions
├── dashboard/            # Plotly Dash / Streamlit dashboard code
├── reports/              # Auto-generated quality & validation reports
├── scripts/
│   ├── data_ingestion.py # Load all CSVs, profile, generate reports
│   └── live_nav_fetch.py # Fetch live NAV from mfapi.in
├── requirements.txt
└── README.md
```

---

## 📊 Datasets (10 CSVs)

| # | File | Description |
|---|------|-------------|
| 01 | `fund_master.csv` | Fund metadata — house, category, risk, expense ratio |
| 02 | `nav_history.csv` | Daily NAV history per scheme |
| 03 | `aum_by_fund_house.csv` | Monthly AUM aggregated by fund house |
| 04 | `monthly_sip_inflows.csv` | Industry-level SIP inflow data |
| 05 | `category_inflows.csv` | Net inflows by fund category |
| 06 | `industry_folio_count.csv` | Total folios across equity/debt/hybrid |
| 07 | `scheme_performance.csv` | Risk-adjusted returns, Sharpe, beta, alpha |
| 08 | `investor_transactions.csv` | ~3 M transaction records with demographics |
| 09 | `portfolio_holdings.csv` | Stock-level holdings per fund |
| 10 | `benchmark_indices.csv` | NIFTY50 / NIFTY100 daily close values |

---

## 🚀 Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run data ingestion (phases 3, 6, 7)
python scripts/data_ingestion.py

# 4. Fetch live NAV data (phases 4, 5)
python scripts/live_nav_fetch.py
```

---

## 📋 Day 1 Deliverables

- [x] Project structure initialized
- [x] `data_ingestion.py` — loads all 10 CSVs, profiles, generates quality report
- [x] `live_nav_fetch.py` — fetches live NAV for 6 funds via mfapi.in
- [x] `reports/data_quality_summary.txt` — missing values, dtypes, duplicates
- [x] `reports/amfi_validation.txt` — AMFI code cross-validation
- [x] `requirements.txt` — full dependency list

---

## 🔗 API Reference

Live NAV data sourced from [mfapi.in](https://www.mfapi.in/) (free, no auth required).

```
GET https://api.mfapi.in/mf/{amfi_code}
```

---

## 👤 Author

Mutual Fund Analytics Internship — Bluestock Fintech
