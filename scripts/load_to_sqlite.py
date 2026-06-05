"""
=============================================================
  Mutual Fund Analytics — Load Cleaned Data into SQLite
  Day 2 | Task 5
=============================================================
  Uses native sqlite3 (pandas 3.x compatible).
  DB: bluestock_mf.db
=============================================================
"""
import os
import sqlite3
import pandas as pd
from datetime import datetime

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
SQL_DIR       = os.path.join(BASE_DIR, "sql")
DB_PATH       = os.path.join(BASE_DIR, "bluestock_mf.db")


def get_con():
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = OFF")   # off during bulk load
    return con


def load_csv(name):
    path = os.path.join(PROCESSED_DIR, name)
    if not os.path.exists(path):
        print(f"  [SKIP] {name} — run data_cleaning.py first")
        return None
    df = pd.read_csv(path, low_memory=False)
    print(f"  Read {name}: {len(df):,} rows")
    return df


def apply_schema(con):
    schema_path = os.path.join(SQL_DIR, "schema.sql")
    if not os.path.exists(schema_path):
        print("  [WARN] schema.sql not found — tables created by pandas")
        return
    with open(schema_path, "r", encoding="utf-8") as f:
        sql = f.read()
    con.executescript(sql)
    print("  Schema applied from schema.sql")


def verify(table, expected, con):
    actual = con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
    status = "OK" if actual == expected else f"MISMATCH expected={expected:,}"
    print(f"  {table:<28} DB={actual:>10,}  src={expected:>10,}  {status}")


def fmt_date(series, fmt=None):
    if fmt:
        return pd.to_datetime(series, format=fmt, errors="coerce").dt.strftime("%Y-%m-%d")
    return pd.to_datetime(series, errors="coerce").dt.strftime("%Y-%m-%d")


def build_dim_date(start="2022-01-01", end="2026-12-31"):
    dates = pd.date_range(start, end, freq="D")
    df = pd.DataFrame({
        "date_id"    : dates.strftime("%Y-%m-%d"),
        "year"       : dates.year,
        "quarter"    : dates.quarter,
        "month"      : dates.month,
        "month_name" : dates.strftime("%B"),
        "week"       : dates.isocalendar().week.astype(int),
        "day_of_week": dates.dayofweek,
        "is_weekday" : (dates.dayofweek < 5).astype(int),
    })
    return df


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"=== Day 2: Loading into SQLite ===")
    print(f"DB path: {DB_PATH}\n")

    # Fresh connection
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("  Removed old DB")

    con = get_con()
    apply_schema(con)

    # ── dim_date ──────────────────────────────────────────────
    print("\n[dim_date]  date spine 2022–2026")
    dim_date = build_dim_date()
    dim_date.to_sql("dim_date", con, if_exists="replace", index=False)
    verify("dim_date", len(dim_date), con)

    # ── dim_fund ──────────────────────────────────────────────
    print("\n[dim_fund]")
    fm = load_csv("01_fund_master_clean.csv")
    if fm is not None:
        fm["launch_date"] = fmt_date(fm["launch_date"])
        fm.to_sql("dim_fund", con, if_exists="replace", index=False)
        verify("dim_fund", len(fm), con)

    # ── fact_nav ──────────────────────────────────────────────
    print("\n[fact_nav]")
    nav = load_csv("02_nav_history_clean.csv")
    if nav is not None:
        nav.rename(columns={"date": "date_id"}, inplace=True)
        nav["date_id"] = fmt_date(nav["date_id"])
        nav[["amfi_code", "date_id", "nav"]].to_sql(
            "fact_nav", con, if_exists="replace", index=False)
        verify("fact_nav", len(nav), con)

    # ── fact_aum ──────────────────────────────────────────────
    print("\n[fact_aum]")
    aum = load_csv("03_aum_by_fund_house_clean.csv")
    if aum is not None:
        aum.rename(columns={"date": "date_id"}, inplace=True)
        aum["date_id"] = fmt_date(aum["date_id"])
        aum.to_sql("fact_aum", con, if_exists="replace", index=False)
        verify("fact_aum", len(aum), con)

    # ── sip_inflows ───────────────────────────────────────────
    print("\n[sip_inflows]")
    sip = load_csv("04_monthly_sip_inflows_clean.csv")
    if sip is not None:
        sip["month"] = fmt_date(sip["month"])
        sip.to_sql("sip_inflows", con, if_exists="replace", index=False)
        verify("sip_inflows", len(sip), con)

    # ── category_inflows ──────────────────────────────────────
    print("\n[category_inflows]")
    cat = load_csv("05_category_inflows_clean.csv")
    if cat is not None:
        cat["month"] = fmt_date(cat["month"])
        cat.to_sql("category_inflows", con, if_exists="replace", index=False)
        verify("category_inflows", len(cat), con)

    # ── folio_count ───────────────────────────────────────────
    print("\n[folio_count]")
    fc = load_csv("06_industry_folio_count_clean.csv")
    if fc is not None:
        fc["month"] = fmt_date(fc["month"])
        fc.to_sql("folio_count", con, if_exists="replace", index=False)
        verify("folio_count", len(fc), con)

    # ── fact_performance ──────────────────────────────────────
    print("\n[fact_performance]")
    perf = load_csv("07_scheme_performance_clean.csv")
    if perf is not None:
        keep_cols = ["amfi_code","return_1yr_pct","return_3yr_pct","return_5yr_pct",
                     "benchmark_3yr_pct","alpha","beta","sharpe_ratio","sortino_ratio",
                     "std_dev_ann_pct","max_drawdown_pct","aum_crore","expense_ratio_pct",
                     "morningstar_rating","risk_grade"]
        perf[[c for c in keep_cols if c in perf.columns]].to_sql(
            "fact_performance", con, if_exists="replace", index=False)
        verify("fact_performance", len(perf), con)

    # ── fact_transactions ─────────────────────────────────────
    print("\n[fact_transactions]")
    tx = load_csv("08_investor_transactions_clean.csv")
    if tx is not None:
        tx.rename(columns={"transaction_date": "date_id"}, inplace=True)
        tx["date_id"] = fmt_date(tx["date_id"])
        tx.to_sql("fact_transactions", con, if_exists="replace", index=False)
        verify("fact_transactions", len(tx), con)

    # ── portfolio_holdings ────────────────────────────────────
    print("\n[portfolio_holdings]")
    ph = load_csv("09_portfolio_holdings_clean.csv")
    if ph is not None:
        ph["portfolio_date"] = fmt_date(ph["portfolio_date"])
        ph.to_sql("portfolio_holdings", con, if_exists="replace", index=False)
        verify("portfolio_holdings", len(ph), con)

    # ── benchmark_indices ─────────────────────────────────────
    print("\n[benchmark_indices]")
    bi = load_csv("10_benchmark_indices_clean.csv")
    if bi is not None:
        bi.rename(columns={"date": "date_id"}, inplace=True)
        bi["date_id"] = fmt_date(bi["date_id"])
        bi.to_sql("benchmark_indices", con, if_exists="replace", index=False)
        verify("benchmark_indices", len(bi), con)

    con.commit()
    con.close()

    size_mb = os.path.getsize(DB_PATH) / 1e6
    print(f"\nDB size : {size_mb:.2f} MB")
    print("Day 2 — SQLite Load Complete!")
