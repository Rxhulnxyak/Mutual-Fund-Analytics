-- =============================================================
--  Mutual Fund Analytics — 10 Analytical SQL Queries
--  Day 2 | Task 6
--  DB: bluestock_mf.db
-- =============================================================

-- ── Q1: Top 5 funds by AUM (crore) ───────────────────────────
-- Business: Identify the largest schemes by assets under management
SELECT
    f.scheme_name,
    f.fund_house,
    f.category,
    p.aum_crore,
    p.morningstar_rating
FROM fact_performance  p
JOIN dim_fund          f ON f.amfi_code = p.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;


-- ── Q2: Average NAV per month per fund (last 12 months) ───────
-- Business: Track monthly NAV trend for each scheme
SELECT
    f.scheme_name,
    strftime('%Y-%m', n.date_id)  AS month,
    ROUND(AVG(n.nav), 4)          AS avg_nav,
    ROUND(MIN(n.nav), 4)          AS min_nav,
    ROUND(MAX(n.nav), 4)          AS max_nav
FROM fact_nav  n
JOIN dim_fund  f ON f.amfi_code = n.amfi_code
WHERE n.date_id >= date('now','-12 months')
GROUP BY f.scheme_name, month
ORDER BY f.scheme_name, month;


-- ── Q3: SIP YoY growth (crore) ────────────────────────────────
-- Business: Measure industry SIP growth year-over-year
SELECT
    strftime('%Y', month) AS year,
    ROUND(SUM(sip_inflow_crore), 2)          AS total_sip_crore,
    ROUND(AVG(active_sip_accounts_crore), 3) AS avg_active_accounts_crore,
    ROUND(SUM(new_sip_accounts_lakh), 2)     AS total_new_sips_lakh
FROM sip_inflows
GROUP BY year
ORDER BY year;


-- ── Q4: Total transactions and amount by state ────────────────
-- Business: Understand geographic investor concentration
SELECT
    state,
    COUNT(*)                            AS total_transactions,
    ROUND(SUM(amount_inr)/1e7, 2)      AS total_amount_crore,
    COUNT(DISTINCT investor_id)         AS unique_investors,
    ROUND(AVG(amount_inr), 2)          AS avg_transaction_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_transactions DESC;


-- ── Q5: Funds with expense_ratio < 1% (low-cost funds) ────────
-- Business: Screen for cost-efficient direct/index funds
SELECT
    f.scheme_name,
    f.fund_house,
    f.category,
    f.plan,
    f.expense_ratio_pct,
    p.return_3yr_pct,
    p.sharpe_ratio
FROM dim_fund         f
JOIN fact_performance p ON p.amfi_code = f.amfi_code
WHERE f.expense_ratio_pct < 1.0
ORDER BY f.expense_ratio_pct ASC;


-- ── Q6: Best risk-adjusted funds (top Sharpe ratio) ──────────
-- Business: Identify funds delivering most return per unit of risk
SELECT
    f.scheme_name,
    f.fund_house,
    f.category,
    p.sharpe_ratio,
    p.sortino_ratio,
    p.alpha,
    p.beta,
    p.return_3yr_pct
FROM fact_performance p
JOIN dim_fund         f ON f.amfi_code = p.amfi_code
WHERE p.sharpe_ratio IS NOT NULL
ORDER BY p.sharpe_ratio DESC
LIMIT 10;


-- ── Q7: Category-wise net inflow trend ───────────────────────
-- Business: See which fund categories are attracting/losing money
SELECT
    category,
    strftime('%Y', month)               AS year,
    ROUND(SUM(net_inflow_crore), 2)    AS annual_net_inflow_crore,
    COUNT(*)                            AS months_reported
FROM category_inflows
GROUP BY category, year
ORDER BY year, annual_net_inflow_crore DESC;


-- ── Q8: SIP vs Lumpsum vs Redemption monthly breakdown ────────
-- Business: Understand transaction type mix over time
SELECT
    strftime('%Y-%m', date_id)   AS month,
    transaction_type,
    COUNT(*)                     AS txn_count,
    ROUND(SUM(amount_inr)/1e7,2) AS total_crore
FROM fact_transactions
GROUP BY month, transaction_type
ORDER BY month, transaction_type;


-- ── Q9: Top 10 most-held stocks across all funds ──────────────
-- Business: Identify concentration risk in underlying stocks
SELECT
    stock_symbol,
    stock_name,
    sector,
    COUNT(DISTINCT amfi_code)        AS funds_holding,
    ROUND(AVG(weight_pct), 2)       AS avg_weight_pct,
    ROUND(SUM(market_value_cr), 2)  AS total_market_value_cr
FROM portfolio_holdings
GROUP BY stock_symbol
ORDER BY funds_holding DESC, total_market_value_cr DESC
LIMIT 10;


-- ── Q10: Fund AUM growth – top 5 fund houses over time ────────
-- Business: Track which fund houses are gaining/losing market share
SELECT
    a.fund_house,
    a.date_id                           AS snapshot_date,
    ROUND(a.aum_crore, 0)              AS aum_crore,
    a.num_schemes,
    ROUND(
        100.0 * a.aum_crore / SUM(a.aum_crore) OVER (PARTITION BY a.date_id),
    2) AS market_share_pct
FROM fact_aum a
WHERE a.fund_house IN (
    SELECT fund_house
    FROM fact_aum
    GROUP BY fund_house
    ORDER BY SUM(aum_crore) DESC
    LIMIT 5
)
ORDER BY a.date_id, a.aum_crore DESC;
