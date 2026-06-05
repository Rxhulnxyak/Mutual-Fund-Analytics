# Mutual Fund Analytics Dashboard

> **Bluestock Fintech Internship Capstone** — End-to-end mutual fund data pipeline, SQL database, EDA, performance analytics, interactive dashboard, and advanced risk metrics.

---

## 📁 Project Structure

```
mutual_fund_analytics/
├── data/
│   ├── raw/                          # 10 original CSVs + PDF brief
│   └── processed/                    # 10 cleaned CSVs + derived outputs
│       ├── fund_cagr.csv
│       ├── fund_risk_metrics.csv
│       ├── alpha_beta.csv
│       ├── fund_scorecard.csv
│       ├── var_cvar_report.csv
│       ├── cohort_analysis.csv
│       ├── sip_continuity.csv
│       ├── sector_hhi.csv
│       └── fund_recommendations.csv
├── notebooks/
│   ├── EDA_Analysis.ipynb
│   ├── Performance_Analytics.ipynb
│   └── Advanced_Analytics.ipynb
├── sql/
│   ├── schema.sql                    # SQLite star schema (DDL)
│   └── queries.sql                   # 10 analytical SQL queries
├── dashboard/
│   └── app.py                        # Streamlit 4-page dashboard
├── reports/
│   ├── charts/                       # 30+ exported PNG charts
│   │   ├── Page1_IndustryOverview.png
│   │   ├── Page2_FundPerformance.png
│   │   ├── Page3_InvestorAnalytics.png
│   │   └── Page4_SIPMarketTrends.png
│   ├── data_quality_summary.txt
│   ├── cleaning_log.txt
│   ├── eda_findings.txt
│   ├── performance_insights.txt
│   └── advanced_insights.txt
├── scripts/
│   ├── data_ingestion.py             # Day 1: Load + profile all CSVs
│   ├── live_nav_fetch.py             # Day 1: Live NAV from mfapi.in
│   ├── data_cleaning.py              # Day 2: Clean all 10 datasets
│   ├── load_to_sqlite.py             # Day 2: ETL into SQLite
│   ├── eda_analysis.py               # Day 3: 17 EDA charts
│   ├── build_notebook.py             # Day 3: Build EDA notebook
│   ├── performance_analytics.py      # Day 4: CAGR, Sharpe, Alpha, Scorecard
│   ├── build_perf_notebook.py        # Day 4: Build performance notebook
│   ├── export_dashboard_pages.py     # Day 5: Export 4 dashboard PNGs
│   ├── advanced_analytics.py         # Day 6: VaR, Rolling Sharpe, HHI, Cohorts
│   ├── build_advanced_notebook.py    # Day 6: Build advanced notebook
│   └── recommender.py               # Day 6: CLI fund recommender
├── bluestock_mf.db                   # SQLite database (5.83 MB)
├── data_dictionary.md
├── requirements.txt
└── README.md
```

---

## 📊 Datasets (10 CSVs)

| # | File | Rows | Description |
|---|------|------|-------------|
| 01 | `fund_master.csv` | 40 | Fund metadata — house, category, risk, expense ratio |
| 02 | `nav_history.csv` | 64,320 | Daily NAV per scheme (forward-filled) |
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

**Star Schema:** `dim_fund` + `dim_date` → `fact_nav`, `fact_transactions`, `fact_performance`, `fact_aum`, `sip_inflows`, `category_inflows`, `folio_count`, `portfolio_holdings`, `benchmark_indices`

---

## 🏆 Fund Scorecard — Top 10

| Rank | Fund | AMC | 3yr CAGR | Sharpe | Score |
|------|------|-----|----------|--------|-------|
| 1 | ICICI Pru Midcap Fund | ICICI Prudential | 31.8% | 0.883 | 100.0 |
| 2 | Axis Midcap Fund | Axis MF | 35.1% | 0.731 | 96.3 |
| 3 | HDFC Mid-Cap Opportunities | HDFC MF | 32.4% | 0.808 | 94.6 |
| 4 | Mirae Asset Large Cap | Mirae Asset | 34.0% | 1.068 | 94.0 |
| 5 | Kotak Flexicap Fund | Kotak MF | 29.6% | 0.966 | 91.9 |

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/Rxhulnxyak/Mutual-Fund-Analytics.git
cd Mutual-Fund-Analytics/mutual_fund_analytics

# Install dependencies
pip install -r requirements.txt

# Run full pipeline
python scripts/data_ingestion.py        # Day 1
python scripts/data_cleaning.py         # Day 2
python scripts/load_to_sqlite.py        # Day 2
python scripts/eda_analysis.py          # Day 3
python scripts/performance_analytics.py # Day 4
python scripts/advanced_analytics.py    # Day 6

# Launch Dashboard
streamlit run dashboard/app.py          # → http://localhost:8501

# Fund Recommender
python scripts/recommender.py           # All risk tiers
python scripts/recommender.py --risk High   # High risk only
```

---

## 📅 Progress Log

| Day | Task | Status | Key Deliverables |
|-----|------|--------|-----------------|
| Day 1 | Project setup, data ingestion, live NAV | ✅ | `data_ingestion.py`, `live_nav_fetch.py` |
| Day 2 | Data cleaning, SQLite star schema, SQL queries | ✅ | `bluestock_mf.db`, `schema.sql`, `queries.sql` |
| Day 3 | EDA — 17 charts, 10 business findings | ✅ | `EDA_Analysis.ipynb`, 17 PNGs |
| Day 4 | Performance analytics — CAGR, Sharpe, Alpha, Scorecard | ✅ | `Performance_Analytics.ipynb`, 10 PNGs, 4 CSVs |
| Day 5 | Streamlit dashboard — 4 pages, Bluestock theme | ✅ | `dashboard/app.py`, 4 page PNGs |
| Day 6 | Advanced analytics — VaR, Rolling Sharpe, HHI, Recommender | ✅ | `Advanced_Analytics.ipynb`, `recommender.py`, 5 PNGs |

---

## 💡 Key Insights

| # | Insight |
|---|---------|
| 1 | Large-cap NAV grew 15–25% in 2023 bull run, corrected H2 2024 |
| 2 | SBI MF leads AUM at ~₹6L Cr; top 3 houses = ~45% of industry |
| 3 | ICICI Pru Midcap Fund scores 100/100 on composite scorecard |
| 4 | ABSL Small Cap has highest VaR(95%) = -2.39%/day — highest tail risk |
| 5 | SIP continuity rate only ~2% — major investor retention opportunity |
| 6 | 9 funds show HIGH sector HHI concentration (>15%) |
| 7 | T30 metros account for >80% of invested amount |
| 8 | Rolling Sharpe clearly exposes 2022 bear, 2023 bull, 2024 correction cycles |

---

## 🔗 Links

- **Dashboard:** `streamlit run dashboard/app.py` → `http://localhost:8501`
- **GitHub:** [Rxhulnxyak/Mutual-Fund-Analytics](https://github.com/Rxhulnxyak/Mutual-Fund-Analytics)
- **Live NAV API:** [mfapi.in](https://www.mfapi.in/)
