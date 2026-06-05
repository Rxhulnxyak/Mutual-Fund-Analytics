# Data Dictionary — Mutual Fund Analytics
**Project:** Bluestock Fintech Capstone | **DB:** `bluestock_mf.db` | **Updated:** Day 2

---

## 01 · `dim_fund` / `01_fund_master_clean.csv`
> One row per AMFI-registered mutual fund scheme.

| Column | Type | Description |
|--------|------|-------------|
| `amfi_code` | INTEGER (PK) | Unique AMFI scheme code assigned by SEBI/AMFI |
| `fund_house` | TEXT | Asset Management Company name (e.g., SBI Mutual Fund) |
| `scheme_name` | TEXT | Full SEBI-registered scheme name |
| `category` | TEXT | Broad category: Equity / Debt / Hybrid |
| `sub_category` | TEXT | SEBI sub-category: Large Cap / Mid Cap / Small Cap / Liquid etc. |
| `plan` | TEXT | `Regular` (distributor) or `Direct` (investor-bought) |
| `launch_date` | DATE | Scheme inception date |
| `benchmark` | TEXT | Benchmark index (e.g., NIFTY 100 TRI) |
| `expense_ratio_pct` | REAL | Annual fee as % of AUM; range [0.1, 2.5] |
| `exit_load_pct` | REAL | Redemption penalty % (0 = no load) |
| `min_sip_amount` | REAL | Minimum monthly SIP amount (INR) |
| `min_lumpsum_amount` | REAL | Minimum one-time investment (INR) |
| `fund_manager` | TEXT | Lead fund manager name |
| `risk_category` | TEXT | SEBI risk label: Low / Moderate / Moderately High / High / Very High |
| `sebi_category_code` | TEXT | SEBI internal category code (e.g., EC01 = Large Cap Equity) |

---

## 02 · `fact_nav` / `02_nav_history_clean.csv`
> Daily Net Asset Value per scheme. Forward-filled for weekends/holidays.

| Column | Type | Description |
|--------|------|-------------|
| `amfi_code` | INTEGER (FK → dim_fund) | Scheme identifier |
| `date` / `date_id` | DATE | NAV date (YYYY-MM-DD) |
| `nav` | REAL | NAV in INR; always > 0 |

**Cleaning notes:** Duplicates removed on `(amfi_code, date)`; NAV forward-filled across all calendar days per fund.

---

## 03 · `fact_aum` / `03_aum_by_fund_house_clean.csv`
> Monthly AUM snapshot aggregated at fund-house level.

| Column | Type | Description |
|--------|------|-------------|
| `date` / `date_id` | DATE | Month-end snapshot date |
| `fund_house` | TEXT | AMC name |
| `aum_lakh_crore` | REAL | AUM in lakh crore INR |
| `aum_crore` | REAL | AUM in crore INR |
| `num_schemes` | INTEGER | Number of active schemes |

---

## 04 · `sip_inflows` / `04_monthly_sip_inflows_clean.csv`
> Industry-level SIP statistics by month.

| Column | Type | Description |
|--------|------|-------------|
| `month` | DATE | Month (YYYY-MM) |
| `sip_inflow_crore` | REAL | Total SIP inflows in crore INR |
| `active_sip_accounts_crore` | REAL | Active SIP accounts in crore |
| `new_sip_accounts_lakh` | REAL | New SIP registrations in lakh |
| `sip_aum_lakh_crore` | REAL | Total SIP AUM in lakh crore INR |
| `yoy_growth_pct` | REAL | Year-on-year SIP growth % (may be NULL for first year) |

---

## 05 · `category_inflows` / `05_category_inflows_clean.csv`
> Monthly net inflows by fund category.

| Column | Type | Description |
|--------|------|-------------|
| `month` | DATE | Month (YYYY-MM) |
| `category` | TEXT | Fund category (Large Cap / Mid Cap / Small Cap etc.) |
| `net_inflow_crore` | REAL | Net inflow (positive = buy pressure, negative = redemptions) |

---

## 06 · `folio_count` / `06_industry_folio_count_clean.csv`
> Monthly industry folio count by asset class.

| Column | Type | Description |
|--------|------|-------------|
| `month` | DATE | Month (YYYY-MM) |
| `total_folios_crore` | REAL | Total investor folios in crore |
| `equity_folios_crore` | REAL | Equity-category folios |
| `debt_folios_crore` | REAL | Debt-category folios |
| `hybrid_folios_crore` | REAL | Hybrid-category folios |
| `others_folios_crore` | REAL | Other-category folios |

---

## 07 · `fact_performance` / `07_scheme_performance_clean.csv`
> Risk-adjusted return metrics per scheme (point-in-time snapshot).

| Column | Type | Description |
|--------|------|-------------|
| `amfi_code` | INTEGER (FK) | Scheme identifier |
| `scheme_name` | TEXT | Scheme name |
| `fund_house` | TEXT | AMC name |
| `category` | TEXT | Fund category |
| `plan` | TEXT | Regular / Direct |
| `return_1yr_pct` | REAL | 1-year absolute return % |
| `return_3yr_pct` | REAL | 3-year CAGR % |
| `return_5yr_pct` | REAL | 5-year CAGR % |
| `benchmark_3yr_pct` | REAL | Benchmark 3-year CAGR % |
| `alpha` | REAL | Jensen's Alpha (excess return vs benchmark) |
| `beta` | REAL | Market sensitivity (1 = moves with market) |
| `sharpe_ratio` | REAL | Return per unit of total risk |
| `sortino_ratio` | REAL | Return per unit of downside risk |
| `std_dev_ann_pct` | REAL | Annualised standard deviation % |
| `max_drawdown_pct` | REAL | Maximum peak-to-trough decline % |
| `aum_crore` | REAL | Assets under management (crore INR) |
| `expense_ratio_pct` | REAL | Annual fee %; flagged if outside [0.1, 2.5] |
| `morningstar_rating` | INTEGER | 1–5 star rating |
| `risk_grade` | TEXT | Qualitative risk label |

---

## 08 · `fact_transactions` / `08_investor_transactions_clean.csv`
> Individual investor transaction records (~32,000 rows).

| Column | Type | Description |
|--------|------|-------------|
| `investor_id` | TEXT | Anonymised investor ID (e.g., INV003054) |
| `transaction_date` / `date_id` | DATE | Transaction date |
| `amfi_code` | INTEGER (FK) | Scheme purchased/redeemed |
| `transaction_type` | TEXT | `SIP` / `Lumpsum` / `Redemption` |
| `amount_inr` | REAL | Transaction amount in INR; always > 0 |
| `state` | TEXT | Investor's Indian state |
| `city` | TEXT | Investor's city |
| `city_tier` | TEXT | `T30` (top 30 cities) or `B30` (beyond top 30) |
| `age_group` | TEXT | Age bracket: 18-25 / 26-35 / 36-45 / 46-55 / 56+ |
| `gender` | TEXT | Male / Female |
| `annual_income_lakh` | REAL | Declared annual income in lakh INR |
| `payment_mode` | TEXT | UPI / Net Banking / Cheque / Mandate |
| `kyc_status` | TEXT | `Verified` or `Pending` |

---

## 09 · `portfolio_holdings` / `09_portfolio_holdings_clean.csv`
> Stock-level holdings per fund as of portfolio date.

| Column | Type | Description |
|--------|------|-------------|
| `amfi_code` | INTEGER (FK) | Fund scheme |
| `stock_symbol` | TEXT | NSE ticker symbol (uppercase) |
| `stock_name` | TEXT | Company full name |
| `sector` | TEXT | Industry sector (Banking / IT / Utilities etc.) |
| `weight_pct` | REAL | % of fund portfolio in this stock [0, 100] |
| `market_value_cr` | REAL | Market value of holding in crore INR |
| `current_price_inr` | REAL | Stock price at portfolio date (INR) |
| `portfolio_date` | DATE | Snapshot date for holdings |

---

## 10 · `benchmark_indices` / `10_benchmark_indices_clean.csv`
> Daily closing values for benchmark indices.

| Column | Type | Description |
|--------|------|-------------|
| `date` / `date_id` | DATE | Trading date |
| `index_name` | TEXT | Index name: NIFTY50 / NIFTY100 / NIFTYMIDCAP150 etc. |
| `close_value` | REAL | Index closing value; always > 0 |

---

## Data Quality Summary

| Dataset | Rows (raw) | Rows (clean) | Key Issues |
|---------|-----------|-------------|------------|
| fund_master | 40 | 40 | None — clean dataset |
| nav_history | ~46,000 | ~1.2M (after ffill) | Dates needed parsing; forward-filled weekends |
| aum_by_fund_house | 90 | 90 | None |
| monthly_sip_inflows | 48 | 48 | `yoy_growth_pct` null for first year |
| category_inflows | 144 | 144 | None |
| industry_folio_count | 21 | 21 | None |
| scheme_performance | 40 | 40 | Some expense ratios at boundary |
| investor_transactions | 32,778 | 32,778 | None — already clean |
| portfolio_holdings | 322 | 322 | None |
| benchmark_indices | 8,050 | 8,050 | None |

---

## Star Schema Relationships

```
dim_date ────────────────────────────────────────────────────┐
             ↑               ↑              ↑                 ↑
         fact_nav     fact_transactions  fact_aum   benchmark_indices
             ↓               ↓
         dim_fund ───── fact_performance
             ↓
         portfolio_holdings
```

---

*Source: Bluestock Fintech Capstone Dataset · Day 2 Deliverable*
