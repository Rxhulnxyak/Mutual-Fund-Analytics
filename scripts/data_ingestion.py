"""
=============================================================
  Mutual Fund Analytics — Data Ingestion & Quality Report
  Day 1 | Phase 3, 6, 7
=============================================================
  Datasets (10 CSVs):
    01_fund_master.csv            06_industry_folio_count.csv
    02_nav_history.csv            07_scheme_performance.csv
    03_aum_by_fund_house.csv      08_investor_transactions.csv
    04_monthly_sip_inflows.csv    09_portfolio_holdings.csv
    05_category_inflows.csv       10_benchmark_indices.csv
=============================================================
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime

# ── Paths ────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_FOLDER   = os.path.join(BASE_DIR, "data", "raw")
REPORTS_DIR  = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# ── Column mappings per file (for targeted checks) ───────────
DATE_COLUMNS = {
    "01_fund_master.csv"         : ["launch_date"],
    "02_nav_history.csv"         : ["date"],
    "03_aum_by_fund_house.csv"   : ["date"],
    "04_monthly_sip_inflows.csv" : ["month"],
    "05_category_inflows.csv"    : ["month"],
    "06_industry_folio_count.csv": ["month"],
    "10_benchmark_indices.csv"   : ["date"],
    "08_investor_transactions.csv": ["transaction_date"],
    "09_portfolio_holdings.csv"  : ["portfolio_date"],
}


# ─────────────────────────────────────────────────────────────
#  HELPER: Profile a DataFrame
# ─────────────────────────────────────────────────────────────
def profile_df(df: pd.DataFrame, filename: str) -> dict:
    missing  = df.isnull().sum()
    dups     = int(df.duplicated().sum())
    uniq     = df.nunique()

    return {
        "filename"      : filename,
        "rows"          : df.shape[0],
        "cols"          : df.shape[1],
        "columns"       : list(df.columns),
        "dtypes"        : df.dtypes.to_dict(),
        "missing"       : missing.to_dict(),
        "missing_total" : int(missing.sum()),
        "duplicates"    : dups,
        "unique_counts" : uniq.to_dict(),
        "df"            : df,
    }


# ─────────────────────────────────────────────────────────────
#  HELPER: Console pretty-print
# ─────────────────────────────────────────────────────────────
def print_profile(p: dict):
    sep = "=" * 65
    print(f"\n{sep}")
    print(f"  FILE  : {p['filename']}")
    print(f"  SHAPE : {p['rows']:,} rows  x  {p['cols']} columns")
    print(sep)

    print("  Columns & dtypes:")
    for col, dt in p["dtypes"].items():
        miss = p["missing"].get(col, 0)
        flag = f"  ← {miss:,} MISSING" if miss > 0 else ""
        print(f"    {col:<38} {str(dt):<12}{flag}")

    print(f"\n  Duplicate rows  : {p['duplicates']:,}")
    print(f"  Total NaN cells : {p['missing_total']:,}")

    print("\n  Unique value counts:")
    for col, u in p["unique_counts"].items():
        print(f"    {col:<38} {u:,}")

    print("\n  Sample (first 3 rows):")
    print(p["df"].head(3).to_string())


# ─────────────────────────────────────────────────────────────
#  HELPER: Build text report block
# ─────────────────────────────────────────────────────────────
def build_report_block(p: dict) -> str:
    lines = [
        "=" * 65,
        f"Dataset : {p['filename']}",
        f"Shape   : {p['rows']:,} rows  x  {p['cols']} columns",
        f"Columns : {', '.join(p['columns'])}",
        "-" * 65,
    ]

    # Missing values
    bad = {k: v for k, v in p["missing"].items() if v > 0}
    if bad:
        lines.append("⚠  Missing Values:")
        for col, cnt in bad.items():
            pct = cnt / p["rows"] * 100
            lines.append(f"   - '{col}': {cnt:,} missing ({pct:.1f}%)")
    else:
        lines.append("✓  No missing values")

    # Duplicates
    if p["duplicates"] > 0:
        lines.append(f"⚠  Duplicate rows: {p['duplicates']:,}")
    else:
        lines.append("✓  No duplicate rows")

    # Object columns that might be dates/numerics
    obj_cols = [c for c, dt in p["dtypes"].items() if str(dt) == "object"]
    date_suspects = DATE_COLUMNS.get(p["filename"], [])
    stored_as_obj = [c for c in date_suspects if c in obj_cols]
    if stored_as_obj:
        lines.append(f"⚠  Date cols stored as object: {stored_as_obj}")

    lines.append("")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
#  PHASE 3: Load all CSVs & generate quality report
# ─────────────────────────────────────────────────────────────
def ingest_all_csvs() -> dict:
    csv_files = sorted([f for f in os.listdir(RAW_FOLDER) if f.endswith(".csv")])
    if not csv_files:
        print(f"[WARN] No CSVs found in {RAW_FOLDER}")
        return {}

    print(f"\n🔍 Found {len(csv_files)} CSV file(s)\n")
    all_data   = {}
    report_lines = [
        "MUTUAL FUND ANALYTICS — DATA QUALITY SUMMARY",
        f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Raw Folder: {RAW_FOLDER}",
        "",
    ]

    for filename in csv_files:
        path = os.path.join(RAW_FOLDER, filename)
        try:
            df = pd.read_csv(path, low_memory=False)
            p  = profile_df(df, filename)
            print_profile(p)
            all_data[filename] = p
            report_lines.append(build_report_block(p))
        except Exception as exc:
            msg = f"[ERROR] {filename}: {exc}"
            print(msg)
            report_lines.append(f"Dataset : {filename}\n  ERROR : {exc}\n")

    report_path = os.path.join(REPORTS_DIR, "data_quality_summary.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"\n✅ Quality report → {report_path}")
    return all_data


# ─────────────────────────────────────────────────────────────
#  PHASE 6: Fund Master Analysis
#  Columns: amfi_code, fund_house, scheme_name, category,
#           sub_category, plan, launch_date, benchmark,
#           expense_ratio_pct, exit_load_pct, min_sip_amount,
#           min_lumpsum_amount, fund_manager, risk_category,
#           sebi_category_code
# ─────────────────────────────────────────────────────────────
def analyse_fund_master(all_data: dict):
    key = next((k for k in all_data if "fund_master" in k.lower()), None)
    if not key:
        print("\n[INFO] fund_master CSV not found — skipping Phase 6.")
        return

    fm = all_data[key]["df"]
    sep = "=" * 65
    print(f"\n{sep}\n  PHASE 6 — Fund Master Deep Dive\n{sep}")

    analyses = [
        ("Unique Fund Houses",  "fund_house"),
        ("Categories",          "category"),
        ("Sub-Categories",      "sub_category"),
        ("Risk Categories",     "risk_category"),
        ("SEBI Category Codes", "sebi_category_code"),
        ("Plans (Regular/Direct)", "plan"),
    ]
    for label, col in analyses:
        if col in fm.columns:
            vc = fm[col].value_counts()
            print(f"\n📊 {label} ({fm[col].nunique()} unique):")
            print(vc.to_string())
        else:
            print(f"[WARN] Column '{col}' not found.")

    # Numeric summary
    num_cols = ["expense_ratio_pct", "exit_load_pct",
                "min_sip_amount", "min_lumpsum_amount"]
    num_cols = [c for c in num_cols if c in fm.columns]
    if num_cols:
        print("\n📊 Numeric Columns — Summary Statistics:")
        print(fm[num_cols].describe().round(2).to_string())


# ─────────────────────────────────────────────────────────────
#  PHASE 7: Validate AMFI Codes
#  fund_master (amfi_code)  ↔  nav_history (amfi_code)
# ─────────────────────────────────────────────────────────────
def validate_amfi_codes(all_data: dict):
    m_key = next((k for k in all_data if "fund_master"  in k.lower()), None)
    n_key = next((k for k in all_data if "nav_history"  in k.lower()), None)
    t_key = next((k for k in all_data if "investor_transactions" in k.lower()), None)

    sep = "=" * 65
    print(f"\n{sep}\n  PHASE 7 — AMFI Code Validation\n{sep}")

    report_lines = [
        "AMFI Code Validation Report",
        f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    if m_key and n_key:
        fm = all_data[m_key]["df"]
        nv = all_data[n_key]["df"]

        master_codes  = set(fm["amfi_code"].dropna().astype(int))
        nav_codes     = set(nv["amfi_code"].dropna().astype(int))
        missing_in_nav = master_codes - nav_codes
        extra_in_nav   = nav_codes    - master_codes

        print(f"  Master codes (fund_master) : {len(master_codes):,}")
        print(f"  NAV codes (nav_history)    : {len(nav_codes):,}")
        print(f"  Missing in NAV             : {len(missing_in_nav)}")
        print(f"  Extra in NAV               : {len(extra_in_nav)}")

        report_lines += [
            f"fund_master  codes : {len(master_codes)}",
            f"nav_history  codes : {len(nav_codes)}",
            f"Missing in NAV     : {len(missing_in_nav)}",
            f"Extra in NAV       : {len(extra_in_nav)}",
            "",
            "Missing AMFI codes (in master but not in NAV):",
            str(sorted(missing_in_nav)),
            "",
            "Extra AMFI codes (in NAV but not in master):",
            str(sorted(extra_in_nav)),
            "",
        ]
    else:
        msg = "[SKIP] Need both fund_master + nav_history for full AMFI validation."
        print(msg)
        report_lines.append(msg)

    # Cross-check with investor transactions
    if m_key and t_key:
        fm = all_data[m_key]["df"]
        tx = all_data[t_key]["df"]
        master_codes  = set(fm["amfi_code"].dropna().astype(int))
        txn_codes     = set(tx["amfi_code"].dropna().astype(int))
        orphan_txns   = txn_codes - master_codes

        print(f"\n  Transaction codes not in master : {len(orphan_txns)}")
        report_lines += [
            "Transaction AMFI codes not in fund_master:",
            str(sorted(orphan_txns)),
        ]

    report_path = os.path.join(REPORTS_DIR, "amfi_validation.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"\n✅ AMFI validation report → {report_path}")


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Mutual Fund Analytics — Data Ingestion Pipeline")
    print(f"   Raw folder : {RAW_FOLDER}\n")

    all_data = ingest_all_csvs()

    if all_data:
        analyse_fund_master(all_data)
        validate_amfi_codes(all_data)

    print("\n🏁 Day 1 — Data Ingestion Complete!\n")
