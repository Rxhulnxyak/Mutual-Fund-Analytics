"""
Fund Recommender — Day 6
Usage:
  python scripts/recommender.py
  python scripts/recommender.py --risk High
  python scripts/recommender.py --risk Low
"""
import os, sys, argparse
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(BASE, "data", "processed")

def p(f): return os.path.join(PROC, f)

RISK_MAP = {
    "Low"      : ["Low", "Moderate"],
    "Moderate" : ["Moderate", "Moderately High"],
    "High"     : ["High", "Very High", "Moderately High"],
}

def recommend(risk_appetite: str = "Moderate", top_n: int = 3) -> pd.DataFrame:
    sc   = pd.read_csv(p("fund_scorecard.csv"))
    fm   = pd.read_csv(p("01_fund_master_clean.csv"))
    risk = pd.read_csv(p("fund_risk_metrics.csv"))
    var  = pd.read_csv(p("var_cvar_report.csv"))

    risk_grades = RISK_MAP.get(risk_appetite, RISK_MAP["Moderate"])

    fm["scheme_short"] = fm["scheme_name"].str.split(" - ").str[0].str[:30]
    var["scheme_short"] = var["scheme_short"].str[:30]

    # Merge on scheme_short (scorecard doesn't carry amfi_code)
    sc = sc.merge(fm[["scheme_short","risk_category","expense_ratio_pct"]].drop_duplicates("scheme_short"),
                  on="scheme_short", how="left")
    sc = sc.merge(var[["scheme_short","VaR_95_daily_pct","CVaR_95_daily_pct"]].drop_duplicates("scheme_short"),
                  on="scheme_short", how="left")

    filtered = sc[sc["risk_category"].isin(risk_grades)].copy()

    if len(filtered) == 0:
        print(f"  [WARN] No funds found for risk={risk_appetite}, showing all funds.")
        filtered = sc.copy()

    top = filtered.sort_values("sharpe_ratio", ascending=False).head(top_n)

    cols = ["rank","scheme_short","fund_house","sub_category","risk_category",
            "cagr_3yr","sharpe_ratio","alpha","expense_ratio_pct","VaR_95_daily_pct","score_100"]
    result = top[[c for c in cols if c in top.columns]].reset_index(drop=True)
    result.index += 1
    return result


def main():
    parser = argparse.ArgumentParser(description="Mutual Fund Recommender")
    parser.add_argument("--risk", choices=["Low","Moderate","High"], default=None)
    parser.add_argument("--top",  type=int, default=3)
    args = parser.parse_args()

    if args.risk:
        # Single recommendation
        appetites = [args.risk]
    else:
        # Interactive mode
        appetites = ["Low", "Moderate", "High"]

    BORDER = "=" * 65

    for appetite in appetites:
        print(f"\n{BORDER}")
        print(f"  FUND RECOMMENDATION — Risk Appetite: {appetite.upper()}")
        print(BORDER)

        recs = recommend(appetite, args.top)

        if recs.empty:
            print("  No recommendations found.")
            continue

        def fmt(val, spec=""):
            try: return format(float(val), spec)
            except: return str(val)

        for i, row in recs.iterrows():
            print(f"\n  #{i} — {row.get('scheme_short','N/A')}")
            print(f"       AMC        : {row.get('fund_house','N/A')}")
            print(f"       Category   : {row.get('sub_category','N/A')}")
            print(f"       Risk Grade : {row.get('risk_category','N/A')}")
            print(f"       3yr CAGR   : {fmt(row.get('cagr_3yr'), '.1f')}%")
            print(f"       Sharpe     : {fmt(row.get('sharpe_ratio'), '.3f')}")
            print(f"       Alpha      : {fmt(row.get('alpha'), '.2f')}%")
            print(f"       Expense    : {fmt(row.get('expense_ratio_pct'), '.2f')}%")
            print(f"       VaR(95%)   : {fmt(row.get('VaR_95_daily_pct'), '.3f')}% / day")
            print(f"       Score      : {fmt(row.get('score_100'), '.1f')}/100")

        print(f"\n  {BORDER}")
        print(f"  WHY THESE FUNDS?")
        print(f"  Ranked by Sharpe ratio within '{appetite}' risk grades.")
        print(f"  Higher Sharpe = better return per unit of risk taken.")
        print(f"  {BORDER}")

    # Also save recommendations as CSV
    all_recs = []
    for appetite in ["Low","Moderate","High"]:
        recs = recommend(appetite, 3)
        recs["recommended_for"] = appetite
        all_recs.append(recs)
    out = pd.concat(all_recs, ignore_index=True)
    out_path = os.path.join(PROC, "fund_recommendations.csv")
    out.to_csv(out_path, index=False)
    print(f"\n  Saved: {out_path}")


if __name__ == "__main__":
    main()
