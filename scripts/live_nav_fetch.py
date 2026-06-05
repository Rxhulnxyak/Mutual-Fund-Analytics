"""
=============================================================
  Mutual Fund Analytics — Live NAV Fetcher
  Day 1 | Phase 4 & 5
=============================================================
  API  : https://api.mfapi.in/mf/{amfi_code}
  Saves: data/raw/{fund_name}.csv
         data/raw/combined_nav_history.csv
=============================================================
"""

import os
import time
import requests
import pandas as pd
from datetime import datetime

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_FOLDER = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_FOLDER, exist_ok=True)

BASE_URL = "https://api.mfapi.in/mf/{code}"

# ── Phase 4: Single test fund ──────────────────────────────
TEST_FUND = {"name": "HDFC_Top100", "code": 125497}

# ── Phase 5: Five required blue-chip funds ─────────────────
FUNDS = {
    "SBI_Bluechip"    : 119551,
    "ICICI_Bluechip"  : 120503,
    "Nippon_LargeCap" : 118632,
    "Axis_Bluechip"   : 119092,
    "Kotak_Bluechip"  : 120841,
}


# ─────────────────────────────────────────────────────────────
def fetch_fund_nav(name: str, code: int, retries: int = 3) -> pd.DataFrame | None:
    url = BASE_URL.format(code=code)
    print(f"\n📡 [{name}]  AMFI: {code}  →  {url}")

    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            data = r.json()

            meta = data.get("meta", {})
            print(f"   Fund       : {meta.get('fund_name', 'N/A')}")
            print(f"   Scheme     : {meta.get('scheme_name', 'N/A')}")
            print(f"   Type/Cat   : {meta.get('scheme_type','N/A')} / {meta.get('scheme_category','N/A')}")

            records = data.get("data", [])
            if not records:
                print(f"   [WARN] Empty data for {name}")
                return None

            df = pd.DataFrame(records)
            df.rename(columns={"date": "nav_date", "nav": "nav_value"}, inplace=True)
            df["amfi_code"]  = code
            df["fund_name"]  = name
            df["fetched_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df["nav_value"]  = pd.to_numeric(df["nav_value"], errors="coerce")
            df["nav_date"]   = pd.to_datetime(df["nav_date"], format="%d-%m-%Y", errors="coerce")
            df.sort_values("nav_date", inplace=True)
            df.reset_index(drop=True, inplace=True)

            latest = df.iloc[-1]
            print(f"   Records    : {len(df):,}")
            print(f"   Date Range : {df['nav_date'].min().date()} → {df['nav_date'].max().date()}")
            print(f"   Latest NAV : ₹{latest['nav_value']:.4f}  ({latest['nav_date'].date()})")
            return df

        except requests.exceptions.Timeout:
            print(f"   [Attempt {attempt}/{retries}] Timeout — retrying...")
            time.sleep(2)
        except requests.exceptions.RequestException as exc:
            print(f"   [Attempt {attempt}/{retries}] Error: {exc}")
            time.sleep(2)
        except Exception as exc:
            print(f"   [ERROR] Unexpected: {exc}")
            return None

    print(f"   ❌ Failed after {retries} attempts.")
    return None


def save_csv(df: pd.DataFrame, name: str):
    path = os.path.join(RAW_FOLDER, f"{name}_live_nav.csv")
    df.to_csv(path, index=False)
    print(f"   💾 Saved → {path}")


# ─────────────────────────────────────────────────────────────
#  Phase 4
# ─────────────────────────────────────────────────────────────
def phase4_test():
    print("\n" + "=" * 60)
    print("  PHASE 4 — Test Fetch: HDFC Top 100")
    print("=" * 60)
    df = fetch_fund_nav(TEST_FUND["name"], TEST_FUND["code"])
    if df is not None:
        save_csv(df, TEST_FUND["name"])
    return df


# ─────────────────────────────────────────────────────────────
#  Phase 5
# ─────────────────────────────────────────────────────────────
def phase5_fetch_all():
    print("\n" + "=" * 60)
    print("  PHASE 5 — Fetch 5 Blue-chip Funds")
    print("=" * 60)

    collected, ok, fail = [], 0, 0
    for name, code in FUNDS.items():
        df = fetch_fund_nav(name, code)
        if df is not None:
            save_csv(df, name)
            collected.append(df)
            ok += 1
        else:
            fail += 1
        time.sleep(0.6)

    if collected:
        combined = pd.concat(collected, ignore_index=True)
        path = os.path.join(RAW_FOLDER, "live_combined_nav.csv")
        combined.to_csv(path, index=False)
        print(f"\n✅ Combined → {path}  ({len(combined):,} rows)")

    print(f"\n📈 Result: {ok} succeeded / {fail} failed")


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Starting Live NAV Fetcher...")
    phase4_test()
    phase5_fetch_all()
    print("\n🏁 Live NAV Fetch Complete!\n")
