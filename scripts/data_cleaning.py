"""
=============================================================
  Mutual Fund Analytics — Data Cleaning Pipeline
  Day 2 | Tasks 1–3
=============================================================
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR       = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
REPORTS_DIR   = os.path.join(BASE_DIR, "reports")
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

log_lines = []

def log(msg):
    print(msg)
    log_lines.append(msg)

def save(df, name):
    path = os.path.join(PROCESSED_DIR, name)
    df.to_csv(path, index=False)
    log(f"  --> {name}  ({len(df):,} rows)")
    return df

# ── 01 Fund Master ────────────────────────────────────────────
def clean_fund_master():
    log("\n[01] fund_master.csv")
    df = pd.read_csv(os.path.join(RAW_DIR, "01_fund_master.csv"), low_memory=False)
    df["launch_date"] = pd.to_datetime(df["launch_date"], errors="coerce")
    for col in ["fund_house","scheme_name","category","sub_category","plan",
                "benchmark","fund_manager","risk_category","sebi_category_code"]:
        df[col] = df[col].astype(str).str.strip()
    df["expense_ratio_pct"] = pd.to_numeric(df["expense_ratio_pct"], errors="coerce")
    df["exit_load_pct"]     = pd.to_numeric(df["exit_load_pct"], errors="coerce")
    bad = df[~df["expense_ratio_pct"].between(0.0, 2.5)].shape[0]
    if bad: log(f"  FLAG: {bad} expense_ratio outside [0,2.5]%")
    df.drop_duplicates(subset=["amfi_code"], keep="first", inplace=True)
    df.sort_values("amfi_code", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return save(df, "01_fund_master_clean.csv")

# ── 02 NAV History (Task 1) ───────────────────────────────────
def clean_nav_history():
    log("\n[02] nav_history.csv  (parse dates, forward-fill, dedup, validate NAV>0)")
    df = pd.read_csv(os.path.join(RAW_DIR, "02_nav_history.csv"), low_memory=False)
    before = len(df)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df.dropna(subset=["date"], inplace=True)
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df = df[df["nav"] > 0].copy()
    dups = df.duplicated(subset=["amfi_code","date"]).sum()
    if dups: log(f"  Removed {dups} duplicate (amfi_code, date) rows")
    df.drop_duplicates(subset=["amfi_code","date"], keep="last", inplace=True)
    df.sort_values(["amfi_code","date"], inplace=True)

    # Forward-fill per fund across all calendar days
    full_dates = pd.date_range(df["date"].min(), df["date"].max(), freq="D")
    parts = []
    for code, grp in df.groupby("amfi_code"):
        g = grp.set_index("date").reindex(full_dates)
        g["amfi_code"] = code
        g["nav"] = g["nav"].ffill()
        g.index.name = "date"
        g.reset_index(inplace=True)
        g.dropna(subset=["nav"], inplace=True)
        parts.append(g)
    df2 = pd.concat(parts, ignore_index=True)
    log(f"  {before:,} -> {len(df2):,} rows after forward-fill")
    return save(df2, "02_nav_history_clean.csv")

# ── 03 AUM ────────────────────────────────────────────────────
def clean_aum():
    log("\n[03] aum_by_fund_house.csv")
    df = pd.read_csv(os.path.join(RAW_DIR, "03_aum_by_fund_house.csv"), low_memory=False)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["fund_house"] = df["fund_house"].astype(str).str.strip()
    for col in ["aum_lakh_crore","aum_crore","num_schemes"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.drop_duplicates(inplace=True)
    df.sort_values(["date","fund_house"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return save(df, "03_aum_by_fund_house_clean.csv")

# ── 04 SIP Inflows ────────────────────────────────────────────
def clean_sip_inflows():
    log("\n[04] monthly_sip_inflows.csv")
    df = pd.read_csv(os.path.join(RAW_DIR, "04_monthly_sip_inflows.csv"), low_memory=False)
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m", errors="coerce")
    for col in ["sip_inflow_crore","active_sip_accounts_crore",
                "new_sip_accounts_lakh","sip_aum_lakh_crore","yoy_growth_pct"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df.drop_duplicates(inplace=True)
    df.sort_values("month", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return save(df, "04_monthly_sip_inflows_clean.csv")

# ── 05 Category Inflows ───────────────────────────────────────
def clean_category_inflows():
    log("\n[05] category_inflows.csv")
    df = pd.read_csv(os.path.join(RAW_DIR, "05_category_inflows.csv"), low_memory=False)
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m", errors="coerce")
    df["category"] = df["category"].astype(str).str.strip()
    df["net_inflow_crore"] = pd.to_numeric(df["net_inflow_crore"], errors="coerce")
    df.drop_duplicates(inplace=True)
    df.sort_values(["month","category"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return save(df, "05_category_inflows_clean.csv")

# ── 06 Folio Count ────────────────────────────────────────────
def clean_folio_count():
    log("\n[06] industry_folio_count.csv")
    df = pd.read_csv(os.path.join(RAW_DIR, "06_industry_folio_count.csv"), low_memory=False)
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m", errors="coerce")
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.drop_duplicates(inplace=True)
    df.sort_values("month", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return save(df, "06_industry_folio_count_clean.csv")

# ── 07 Scheme Performance (Task 3) ───────────────────────────
def clean_scheme_performance():
    log("\n[07] scheme_performance.csv  (validate numerics, flag expense anomalies)")
    df = pd.read_csv(os.path.join(RAW_DIR, "07_scheme_performance.csv"), low_memory=False)
    num_cols = ["return_1yr_pct","return_3yr_pct","return_5yr_pct","benchmark_3yr_pct",
                "alpha","beta","sharpe_ratio","sortino_ratio","std_dev_ann_pct",
                "max_drawdown_pct","aum_crore","expense_ratio_pct","morningstar_rating"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # Flag bad expense ratios
    if "expense_ratio_pct" in df.columns:
        bad = df[~df["expense_ratio_pct"].between(0.1, 2.5)]
        if len(bad):
            log(f"  FLAG: {len(bad)} schemes with expense_ratio outside [0.1,2.5]%")
            for _, r in bad.iterrows():
                log(f"    amfi={r['amfi_code']}  expense={r['expense_ratio_pct']}")
    # Flag extreme 1yr returns
    if "return_1yr_pct" in df.columns:
        ext = df[df["return_1yr_pct"].abs() > 100]
        if len(ext): log(f"  FLAG: {len(ext)} schemes |return_1yr|>100%")
    for col in ["scheme_name","fund_house","category","plan","risk_grade"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    df.drop_duplicates(subset=["amfi_code"], keep="first", inplace=True)
    df.sort_values("amfi_code", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return save(df, "07_scheme_performance_clean.csv")

# ── 08 Investor Transactions (Task 2) ────────────────────────
def clean_investor_transactions():
    log("\n[08] investor_transactions.csv  (standardise types, validate amounts, KYC enum)")
    df = pd.read_csv(os.path.join(RAW_DIR, "08_investor_transactions.csv"), low_memory=False)
    before = len(df)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df.dropna(subset=["transaction_date"], inplace=True)
    VALID_TYPES = {"SIP","Lumpsum","Redemption"}
    df["transaction_type"] = df["transaction_type"].astype(str).str.strip()
    # Normalise: SIP (case-insensitive), Lumpsum, Redemption
    type_map = {"sip":"SIP","lumpsum":"Lumpsum","redemption":"Redemption"}
    df["transaction_type"] = df["transaction_type"].str.lower().map(type_map).fillna(df["transaction_type"])
    bad_t = ~df["transaction_type"].isin(VALID_TYPES)
    if bad_t.sum():
        log(f"  FLAG: {bad_t.sum()} invalid transaction_type values -> {df.loc[bad_t,'transaction_type'].unique()}")
    df = df[~bad_t].copy()
    df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")
    df = df[df["amount_inr"] > 0].copy()
    VALID_KYC = {"Verified","Pending"}
    df["kyc_status"] = df["kyc_status"].astype(str).str.strip()
    bad_k = ~df["kyc_status"].isin(VALID_KYC)
    if bad_k.sum(): log(f"  FLAG: {bad_k.sum()} invalid kyc_status values")
    for col in ["state","city","city_tier","age_group","gender","payment_mode"]:
        df[col] = df[col].astype(str).str.strip()
    df["annual_income_lakh"] = pd.to_numeric(df["annual_income_lakh"], errors="coerce")
    df.drop_duplicates(inplace=True)
    df.sort_values(["investor_id","transaction_date"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    log(f"  {before:,} -> {len(df):,} rows")
    return save(df, "08_investor_transactions_clean.csv")

# ── 09 Portfolio Holdings ─────────────────────────────────────
def clean_portfolio_holdings():
    log("\n[09] portfolio_holdings.csv")
    df = pd.read_csv(os.path.join(RAW_DIR, "09_portfolio_holdings.csv"), low_memory=False)
    df["portfolio_date"] = pd.to_datetime(df["portfolio_date"], errors="coerce")
    for col in ["weight_pct","market_value_cr","current_price_inr"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    bad_w = df[~df["weight_pct"].between(0,100)].shape[0]
    if bad_w: log(f"  FLAG: {bad_w} weight_pct outside [0,100]")
    df["stock_symbol"] = df["stock_symbol"].astype(str).str.strip().str.upper()
    df["sector"]       = df["sector"].astype(str).str.strip()
    df.drop_duplicates(inplace=True)
    df.sort_values(["amfi_code","stock_symbol"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return save(df, "09_portfolio_holdings_clean.csv")

# ── 10 Benchmark Indices ──────────────────────────────────────
def clean_benchmark_indices():
    log("\n[10] benchmark_indices.csv")
    df = pd.read_csv(os.path.join(RAW_DIR, "10_benchmark_indices.csv"), low_memory=False)
    df["date"]        = pd.to_datetime(df["date"], errors="coerce")
    df["index_name"]  = df["index_name"].astype(str).str.strip()
    df["close_value"] = pd.to_numeric(df["close_value"], errors="coerce")
    neg = (df["close_value"] <= 0).sum()
    if neg: log(f"  FLAG: {neg} close_value <= 0")
    df.drop_duplicates(subset=["date","index_name"], keep="last", inplace=True)
    df.sort_values(["index_name","date"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return save(df, "10_benchmark_indices_clean.csv")

# ── Main ──────────────────────────────────────────────────────
if __name__ == "__main__":
    log("=== Day 2: Data Cleaning Pipeline ===")
    results = {}
    results["fund_master"]           = clean_fund_master()
    results["nav_history"]           = clean_nav_history()
    results["aum"]                   = clean_aum()
    results["sip_inflows"]           = clean_sip_inflows()
    results["category_inflows"]      = clean_category_inflows()
    results["folio_count"]           = clean_folio_count()
    results["scheme_performance"]    = clean_scheme_performance()
    results["investor_transactions"] = clean_investor_transactions()
    results["portfolio_holdings"]    = clean_portfolio_holdings()
    results["benchmark_indices"]     = clean_benchmark_indices()

    rpt = os.path.join(REPORTS_DIR, "cleaning_log.txt")
    with open(rpt, "w", encoding="utf-8") as f:
        f.write("CLEANING LOG\n")
        f.write(f"Generated: {datetime.now()}\n\n")
        f.write("\n".join(log_lines))
    print(f"\nCleaning log -> {rpt}")
    print("\n=== Summary ===")
    for k, df in results.items():
        print(f"  {k:<30} {len(df):>10,} rows")
    print("\nDay 2 Cleaning Complete!")
