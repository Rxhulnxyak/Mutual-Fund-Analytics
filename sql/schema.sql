-- =============================================================
--  Mutual Fund Analytics — SQLite Star Schema
--  Day 2 | Task 4
--  DB: bluestock_mf.db
-- =============================================================

PRAGMA foreign_keys = ON;

-- ─────────────────────────────────────────────────────────────
--  DIMENSION: dim_fund
--  One row per AMFI scheme
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code           INTEGER PRIMARY KEY,
    fund_house          TEXT    NOT NULL,
    scheme_name         TEXT    NOT NULL,
    category            TEXT,
    sub_category        TEXT,
    plan                TEXT    CHECK(plan IN ('Regular','Direct')),
    launch_date         TEXT,
    benchmark           TEXT,
    expense_ratio_pct   REAL,
    exit_load_pct       REAL,
    min_sip_amount      REAL,
    min_lumpsum_amount  REAL,
    fund_manager        TEXT,
    risk_category       TEXT    CHECK(risk_category IN ('Low','Moderate','Moderately High','High','Very High')),
    sebi_category_code  TEXT
);

-- ─────────────────────────────────────────────────────────────
--  DIMENSION: dim_date
--  Date spine for time-series joins
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS dim_date (
    date_id     TEXT PRIMARY KEY,   -- YYYY-MM-DD
    year        INTEGER,
    quarter     INTEGER,
    month       INTEGER,
    month_name  TEXT,
    week        INTEGER,
    day_of_week INTEGER,
    is_weekday  INTEGER             -- 1=weekday, 0=weekend
);

-- ─────────────────────────────────────────────────────────────
--  FACT: fact_nav
--  Daily NAV per fund
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code   INTEGER NOT NULL REFERENCES dim_fund(amfi_code),
    date_id     TEXT    NOT NULL REFERENCES dim_date(date_id),
    nav         REAL    NOT NULL CHECK(nav > 0),
    UNIQUE(amfi_code, date_id)
);

-- ─────────────────────────────────────────────────────────────
--  FACT: fact_transactions
--  Investor buy/sell/SIP transactions
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_transactions (
    txn_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id         TEXT    NOT NULL,
    date_id             TEXT    NOT NULL REFERENCES dim_date(date_id),
    amfi_code           INTEGER NOT NULL REFERENCES dim_fund(amfi_code),
    transaction_type    TEXT    CHECK(transaction_type IN ('SIP','Lumpsum','Redemption')),
    amount_inr          REAL    CHECK(amount_inr > 0),
    state               TEXT,
    city                TEXT,
    city_tier           TEXT,
    age_group           TEXT,
    gender              TEXT,
    annual_income_lakh  REAL,
    payment_mode        TEXT,
    kyc_status          TEXT    CHECK(kyc_status IN ('Verified','Pending'))
);

-- ─────────────────────────────────────────────────────────────
--  FACT: fact_performance
--  Risk-adjusted returns per scheme
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_performance (
    perf_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code           INTEGER NOT NULL REFERENCES dim_fund(amfi_code),
    return_1yr_pct      REAL,
    return_3yr_pct      REAL,
    return_5yr_pct      REAL,
    benchmark_3yr_pct   REAL,
    alpha               REAL,
    beta                REAL,
    sharpe_ratio        REAL,
    sortino_ratio       REAL,
    std_dev_ann_pct     REAL,
    max_drawdown_pct    REAL,
    aum_crore           REAL,
    expense_ratio_pct   REAL,
    morningstar_rating  INTEGER,
    risk_grade          TEXT
);

-- ─────────────────────────────────────────────────────────────
--  FACT: fact_aum
--  Monthly AUM by fund house
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date_id             TEXT    NOT NULL REFERENCES dim_date(date_id),
    fund_house          TEXT    NOT NULL,
    aum_crore           REAL,
    aum_lakh_crore      REAL,
    num_schemes         INTEGER,
    UNIQUE(date_id, fund_house)
);

-- ─────────────────────────────────────────────────────────────
--  SUPPLEMENTAL: sip_inflows, category_inflows,
--                folio_count, portfolio_holdings, benchmarks
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sip_inflows (
    month                       TEXT PRIMARY KEY,
    sip_inflow_crore            REAL,
    active_sip_accounts_crore   REAL,
    new_sip_accounts_lakh       REAL,
    sip_aum_lakh_crore          REAL,
    yoy_growth_pct              REAL
);

CREATE TABLE IF NOT EXISTS category_inflows (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    month           TEXT,
    category        TEXT,
    net_inflow_crore REAL,
    UNIQUE(month, category)
);

CREATE TABLE IF NOT EXISTS folio_count (
    month                   TEXT PRIMARY KEY,
    total_folios_crore      REAL,
    equity_folios_crore     REAL,
    debt_folios_crore       REAL,
    hybrid_folios_crore     REAL,
    others_folios_crore     REAL
);

CREATE TABLE IF NOT EXISTS portfolio_holdings (
    holding_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code           INTEGER NOT NULL REFERENCES dim_fund(amfi_code),
    stock_symbol        TEXT,
    stock_name          TEXT,
    sector              TEXT,
    weight_pct          REAL,
    market_value_cr     REAL,
    current_price_inr   REAL,
    portfolio_date      TEXT
);

CREATE TABLE IF NOT EXISTS benchmark_indices (
    bench_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    date_id     TEXT NOT NULL REFERENCES dim_date(date_id),
    index_name  TEXT,
    close_value REAL,
    UNIQUE(date_id, index_name)
);

-- ─────────────────────────────────────────────────────────────
--  INDEXES for query performance
-- ─────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_nav_amfi    ON fact_nav(amfi_code);
CREATE INDEX IF NOT EXISTS idx_nav_date    ON fact_nav(date_id);
CREATE INDEX IF NOT EXISTS idx_txn_amfi    ON fact_transactions(amfi_code);
CREATE INDEX IF NOT EXISTS idx_txn_date    ON fact_transactions(date_id);
CREATE INDEX IF NOT EXISTS idx_txn_state   ON fact_transactions(state);
CREATE INDEX IF NOT EXISTS idx_txn_type    ON fact_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_perf_amfi   ON fact_performance(amfi_code);
CREATE INDEX IF NOT EXISTS idx_aum_date    ON fact_aum(date_id);
CREATE INDEX IF NOT EXISTS idx_bench_date  ON benchmark_indices(date_id);
CREATE INDEX IF NOT EXISTS idx_bench_name  ON benchmark_indices(index_name);
