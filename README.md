# Mutual Fund Analytics Dashboard

> **Bluestock Fintech Internship Capstone** — End-to-end mutual fund data pipeline, SQL database, EDA, and interactive dashboard.

---

## 📁 Project Structure

```
mutual_fund_analytics/
├── data/
│   ├── raw/              # 10 original CSV datasets + PDF brief
│   └── processed/        # 10 cleaned & validated CSVs
├── notebooks/
│   └── EDA_Analysis.ipynb
├── sql/
│   ├── schema.sql        # SQLite star schema (DDL)
│   └── queries.sql       # 10 analytical SQL queries
├── dashboard/            # (Day 4+)
├── reports/
│   ├── charts/           # 17 exported PNG charts
│   ├── data_quality_summary.txt
│   ├── amfi_validation.txt
│   ├── cleaning_log.txt
│   └── eda_findings.txt
├── scripts/
│   ├── data_ingestion.py     # Load + profile all 10 CSVs
│   ├── live_nav_fetch.py     # Live NAV from mfapi.in
│   ├── data_cleaning.py      # Clean all 10 CSVs → processed/
│   ├── load_to_sqlite.py     # Load cleaned data into SQLite
│   ├── eda_analysis.py       # Generate 17 EDA charts
│   └── build_notebook.py     # Build EDA_Analysis.ipynb
├── bluestock_mf.db           # SQLite database (5.83 MB)
├── data_dictionary.md        # Column definitions & business rules
├── requirements.txt
└── README.md
```

---

## 📊 Datasets (10 CSVs)

| # | File | Rows | Description |
|---|------|------|-------------|
| 01 | `fund_master.csv` | 40 | Fund metadata — house, category, risk, expense ratio |
| 02 | `nav_history.csv` | 46,000+ | Daily NAV per scheme (64K after forward-fill) |
| 03 | `aum_by_fund_house.csv` | 90 | Monthly AUM by AMC |
| 04 | `monthly_sip_inflows.csv` | 48 | Industry SIP statistics |
| 05 | `category_inflows.csv` | 144 | Net inflows by fund category |
| 06 | `industry_folio_count.csv` | 21 | Total folios by asset class |
| 07 | `scheme_performance.csv` | 40 | Risk-adjusted returns, Sharpe, alpha, beta |
| 08 | `investor_transactions.csv` | 32,778 | SIP / Lumpsum / Redemption transactions |
| 09 | `portfolio_holdings.csv` | 322 | Stock-level holdings per fund |
| 10 | `benchmark_indices.csv` | 8,050 | NIFTY50 / NIFTY100 daily close |

---

## 🗄️ Database — `bluestock_mf.db` (SQLite, 5.83 MB)

**Star Schema:**
```
dim_date ──────────────────────────────────────────┐
              ↑              ↑            ↑          ↑
          fact_nav   fact_transactions  fact_aum  benchmarks
              ↓              ↓
          dim_fund ──── fact_performance
              ↓
          portfolio_holdings
```

**Tables:** `dim_fund`, `dim_date`, `fact_nav`, `fact_transactions`, `fact_performance`, `fact_aum`, `sip_inflows`, `category_inflows`, `folio_count`, `portfolio_holdings`, `benchmark_indices`

---

## 📈 EDA — 10 Key Findings

| # | Finding |
|---|---------|
| 1 | Large-cap NAV grew 15–25% in 2023 bull run, corrected H2 2024 |
| 2 | SBI MF led AUM at ~₹6L Cr; top 3 houses = ~45% of industry |
| 3 | SIP inflows hit all-time highs — structural shift to systematic investing |
| 4 | Large Cap & Flexi Cap attracted highest inflows during bull markets |
| 5 | Investors aged 36–45 = highest SIP amounts; 18–25 = fastest growing |
| 6 | Male investors 65% count; female investors show higher avg ticket size |
| 7 | T30 metros >80% of invested amount; B30 growing steadily |
| 8 | Industry folios doubled — driven by digital adoption and SIP awareness |
| 9 | Large-cap fund returns correlated 0.85+; limited within-category diversification |
| 10 | Financial Services + Banking dominate holdings — concentration risk exists |

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/Rxhulnxyak/Mutual-Fund-Analytics.git
cd Mutual-Fund-Analytics/mutual_fund_analytics

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run pipeline (in order)
python scripts/data_ingestion.py   # Day 1: Load + profile
python scripts/live_nav_fetch.py   # Day 1: Fetch live NAV
python scripts/data_cleaning.py    # Day 2: Clean all CSVs
python scripts/load_to_sqlite.py   # Day 2: Load into SQLite
python scripts/eda_analysis.py     # Day 3: Generate charts
python scripts/build_notebook.py   # Day 3: Build notebook
```

---

## 📅 Progress Log

| Day | Task | Status |
|-----|------|--------|
| Day 1 | Project setup, data ingestion, live NAV fetch, AMFI validation | ✅ |
| Day 2 | Data cleaning, SQLite star schema, 10 SQL queries, data dictionary | ✅ |
| Day 3 | EDA — 17 charts, 10 business findings, Jupyter notebook | ✅ |
| Day 4 | Performance analytics & risk metrics | 🔜 |
| Day 5 | Interactive dashboard (Plotly Dash / Streamlit) | 🔜 |

---

## 🔗 API Reference

Live NAV data sourced from [mfapi.in](https://www.mfapi.in/) — free, no auth required.
```
GET https://api.mfapi.in/mf/{amfi_code}
```

---

## 👤 Author

**Mutual Fund Analytics Internship — Bluestock Fintech**
GitHub: [Rxhulnxyak/Mutual-Fund-Analytics](https://github.com/Rxhulnxyak/Mutual-Fund-Analytics)
