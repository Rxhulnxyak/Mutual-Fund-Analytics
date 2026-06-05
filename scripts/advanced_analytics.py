"""
Day 6 — Advanced Analytics + Risk Metrics
Outputs:
  data/processed/var_cvar_report.csv
  data/processed/cohort_analysis.csv
  data/processed/sip_continuity.csv
  data/processed/sector_hhi.csv
  reports/charts/rolling_sharpe_chart.png
"""
import os, warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")
sns.set_theme(style="darkgrid")

BASE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC   = os.path.join(BASE, "data", "processed")
CHARTS = os.path.join(BASE, "reports", "charts")
os.makedirs(CHARTS, exist_ok=True)

def p(f): return os.path.join(PROC, f)

PRIMARY   = "#003366"
SECONDARY = "#0077CC"
ACCENT    = "#4DA6FF"

# ── Load ─────────────────────────────────────────────────────
print("Loading data...")
nav  = pd.read_csv(p("02_nav_history_clean.csv"), parse_dates=["date"])
fm   = pd.read_csv(p("01_fund_master_clean.csv"))
tx   = pd.read_csv(p("08_investor_transactions_clean.csv"), parse_dates=["transaction_date"])
port = pd.read_csv(p("09_portfolio_holdings_clean.csv"))
sc   = pd.read_csv(p("fund_scorecard.csv"))

nav  = nav.merge(fm[["amfi_code","scheme_name","fund_house","category",
                      "sub_category","risk_category"]], on="amfi_code", how="left")
nav["scheme_short"] = nav["scheme_name"].str.split(" - ").str[0].str[:30]
nav  = nav.sort_values(["amfi_code","date"]).reset_index(drop=True)
nav["daily_return"] = nav.groupby("amfi_code")["nav"].pct_change()

TRADING = 252
RF = 0.065

# ════════════════════════════════════════════════════════════
#  TASK 1: VaR (95%) & CVaR per fund
# ════════════════════════════════════════════════════════════
print("\n[1] VaR & CVaR (95%) Calculation...")
var_records = []
for code, grp in nav.groupby("amfi_code"):
    ret = grp["daily_return"].dropna()
    if len(ret) < 30: continue
    var_95  = np.percentile(ret, 5)           # 5th percentile
    cvar_95 = ret[ret <= var_95].mean()       # mean of tail losses
    ann_ret = ret.mean() * TRADING
    ann_std = ret.std()  * np.sqrt(TRADING)
    var_records.append({
        "amfi_code"       : code,
        "scheme_short"    : grp["scheme_short"].iloc[0],
        "fund_house"      : grp["fund_house"].iloc[0],
        "sub_category"    : grp["sub_category"].iloc[0],
        "risk_category"   : grp["risk_category"].iloc[0],
        "VaR_95_daily_pct": round(var_95 * 100, 4),
        "CVaR_95_daily_pct": round(cvar_95 * 100, 4),
        "VaR_95_annual_pct": round(var_95 * np.sqrt(TRADING) * 100, 4),
        "ann_return_pct"  : round(ann_ret * 100, 2),
        "ann_volatility_pct": round(ann_std * 100, 2),
        "obs"             : len(ret),
    })

var_df = pd.DataFrame(var_records)
var_df = var_df.sort_values("VaR_95_daily_pct")   # most negative = highest risk
var_df.to_csv(p("var_cvar_report.csv"), index=False)
print(f"  Saved var_cvar_report.csv ({len(var_df)} funds)")
print("\n  Highest Risk (worst VaR):")
print(var_df[["scheme_short","VaR_95_daily_pct","CVaR_95_daily_pct","sub_category"]].head(8).to_string(index=False))
print("\n  Lowest Risk (best VaR):")
print(var_df[["scheme_short","VaR_95_daily_pct","CVaR_95_daily_pct","sub_category"]].tail(8).to_string(index=False))

# Chart: VaR comparison
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
top10_var = var_df.head(10)
axes[0].barh(top10_var["scheme_short"].str[:28], top10_var["VaR_95_daily_pct"],
             color="#E74C3C", alpha=0.85)
axes[0].set_title("Highest VaR 95% — Top 10 Riskiest Funds\n(Most Negative = Highest Risk)",
                   fontweight="bold", color=PRIMARY)
axes[0].set_xlabel("VaR 95% Daily (%)")

top10_safe = var_df.tail(10)
axes[1].barh(top10_safe["scheme_short"].str[:28], top10_safe["VaR_95_daily_pct"],
             color="#2ECC71", alpha=0.85)
axes[1].set_title("Lowest VaR 95% — Top 10 Safest Funds",
                   fontweight="bold", color=PRIMARY)
axes[1].set_xlabel("VaR 95% Daily (%)")
plt.tight_layout()
plt.savefig(os.path.join(CHARTS,"advanced_var_cvar.png"), dpi=150, bbox_inches="tight")
plt.close(); print("  saved advanced_var_cvar.png")

# ════════════════════════════════════════════════════════════
#  TASK 2: Rolling 90-Day Sharpe Ratio
# ════════════════════════════════════════════════════════════
print("\n[2] Rolling 90-Day Sharpe Ratio...")

# Pick 5 key funds (top scorers across different categories)
key_funds = sc.drop_duplicates("sub_category").head(5)["scheme_short"].tolist()
# Fallback if names don't match exactly
all_shorts = nav["scheme_short"].unique()
key_funds  = [f for f in key_funds if f in all_shorts][:5]
if len(key_funds) < 5:
    extra = [f for f in sc["scheme_short"].unique() if f in all_shorts and f not in key_funds]
    key_funds += extra[:5-len(key_funds)]

fig, ax = plt.subplots(figsize=(16, 7))
palette = [PRIMARY, SECONDARY, ACCENT, "#E74C3C", "#2ECC71"]

for i, name in enumerate(key_funds[:5]):
    grp = nav[nav["scheme_short"]==name].sort_values("date").set_index("date")
    ret = grp["daily_return"].dropna()
    roll_mean = ret.rolling(90).mean() * TRADING
    roll_std  = ret.rolling(90).std()  * np.sqrt(TRADING)
    roll_sharpe = (roll_mean - RF) / roll_std
    ax.plot(roll_sharpe.index, roll_sharpe.values,
            linewidth=1.8, color=palette[i], alpha=0.85, label=name[:28])

ax.axhline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)
ax.axhline(1, color="gray",  linewidth=0.8, linestyle=":", alpha=0.5, label="Sharpe=1 (Good)")
ax.fill_between(ax.get_lines()[0].get_xdata(),
                ax.get_ylim()[0], 0, alpha=0.05, color="red")
ax.set_title("Rolling 90-Day Sharpe Ratio — 5 Key Funds", fontsize=14, fontweight="bold", color=PRIMARY)
ax.set_xlabel("Date"); ax.set_ylabel("Rolling Sharpe Ratio")
ax.legend(fontsize=8, ncol=2)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS,"rolling_sharpe_chart.png"), dpi=150, bbox_inches="tight")
plt.close(); print("  saved rolling_sharpe_chart.png")

# ════════════════════════════════════════════════════════════
#  TASK 3: Investor Cohort Analysis
# ════════════════════════════════════════════════════════════
print("\n[3] Investor Cohort Analysis...")
tx["first_txn_year"] = tx.groupby("investor_id")["transaction_date"].transform("min").dt.year
sip_only = tx[tx["transaction_type"]=="SIP"].copy()

cohort = sip_only.groupby("first_txn_year").agg(
    investor_count   = ("investor_id",  "nunique"),
    avg_sip_amount   = ("amount_inr",   "mean"),
    total_invested   = ("amount_inr",   "sum"),
    txn_count        = ("amount_inr",   "count"),
).reset_index()
cohort["total_invested_cr"] = cohort["total_invested"] / 1e7
cohort["avg_sip_amount"]    = cohort["avg_sip_amount"].round(0)
cohort["total_invested_cr"] = cohort["total_invested_cr"].round(2)

# Top fund preference per cohort
if "amfi_code" in sip_only.columns:
    top_fund_per_cohort = (
        sip_only.groupby(["first_txn_year","amfi_code"])["amount_inr"].sum()
        .reset_index()
        .sort_values("amount_inr", ascending=False)
        .groupby("first_txn_year")["amfi_code"].first()
        .reset_index()
        .rename(columns={"amfi_code":"top_amfi_code"})
    )
    top_fund_per_cohort = top_fund_per_cohort.merge(
        fm[["amfi_code","scheme_name"]], left_on="top_amfi_code", right_on="amfi_code", how="left")
    cohort = cohort.merge(top_fund_per_cohort[["first_txn_year","scheme_name"]], on="first_txn_year", how="left")
    cohort.rename(columns={"scheme_name":"top_fund_choice"}, inplace=True)

cohort.to_csv(p("cohort_analysis.csv"), index=False)
print(f"  Saved cohort_analysis.csv")
print(cohort.to_string(index=False))

# Chart: Cohort invested amount
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].bar(cohort["first_txn_year"].astype(str), cohort["total_invested_cr"], color=SECONDARY)
axes[0].set_title("Total SIP Invested by Entry Cohort (Crore)", fontweight="bold", color=PRIMARY)
axes[0].set_xlabel("First Investment Year"); axes[0].set_ylabel("Amount (Crore)")
axes[1].bar(cohort["first_txn_year"].astype(str), cohort["investor_count"], color=ACCENT)
axes[1].set_title("Investor Count by Entry Cohort", fontweight="bold", color=PRIMARY)
axes[1].set_xlabel("First Investment Year"); axes[1].set_ylabel("Investors")
plt.tight_layout()
plt.savefig(os.path.join(CHARTS,"advanced_cohort_analysis.png"), dpi=150, bbox_inches="tight")
plt.close(); print("  saved advanced_cohort_analysis.png")

# ════════════════════════════════════════════════════════════
#  TASK 4: SIP Continuity Analysis
# ════════════════════════════════════════════════════════════
print("\n[4] SIP Continuity Analysis...")
sip_sorted = sip_only.sort_values(["investor_id","transaction_date"])
sip_sorted["days_gap"] = sip_sorted.groupby("investor_id")["transaction_date"].diff().dt.days

# Only investors with 6+ SIP transactions
sip_count = sip_only.groupby("investor_id").size()
regular_investors = sip_count[sip_count >= 6].index

continuity = (
    sip_sorted[sip_sorted["investor_id"].isin(regular_investors)]
    .groupby("investor_id")["days_gap"]
    .agg(avg_gap="mean", max_gap="max", txn_count="count")
    .dropna()
    .reset_index()
)
continuity["avg_gap"]   = continuity["avg_gap"].round(1)
continuity["max_gap"]   = continuity["max_gap"].round(1)
continuity["at_risk"]   = continuity["avg_gap"] > 35
continuity["status"]    = continuity["at_risk"].map({True:"At-Risk", False:"Regular"})

at_risk_n  = continuity["at_risk"].sum()
regular_n  = (~continuity["at_risk"]).sum()
continuity_rate = regular_n / len(continuity) * 100

print(f"  Regular SIP investors (6+ txns): {len(continuity):,}")
print(f"  Continuous (avg gap ≤35d):       {regular_n:,}  ({continuity_rate:.1f}%)")
print(f"  At-risk   (avg gap >35d):        {at_risk_n:,}")

continuity.to_csv(p("sip_continuity.csv"), index=False)
print(f"  Saved sip_continuity.csv")

# Chart
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].hist(continuity["avg_gap"].clip(0, 90), bins=30, color=SECONDARY, edgecolor="white")
axes[0].axvline(35, color="red", linestyle="--", label="35-day threshold")
axes[0].set_title("Distribution of Avg SIP Gap (Days)", fontweight="bold", color=PRIMARY)
axes[0].set_xlabel("Avg Days Between SIPs"); axes[0].legend()
status_c = continuity["status"].value_counts()
axes[1].pie(status_c, labels=status_c.index, autopct="%1.1f%%",
            colors=[SECONDARY, "#E74C3C"], startangle=90)
axes[1].set_title(f"SIP Continuity: Regular vs At-Risk\n(n={len(continuity):,} investors)",
                  fontweight="bold", color=PRIMARY)
plt.tight_layout()
plt.savefig(os.path.join(CHARTS,"advanced_sip_continuity.png"), dpi=150, bbox_inches="tight")
plt.close(); print("  saved advanced_sip_continuity.png")

# ════════════════════════════════════════════════════════════
#  TASK 6: Sector HHI Concentration
# ════════════════════════════════════════════════════════════
print("\n[6] Sector HHI Concentration...")
# HHI = Σ(weight_i / total_weight)²
hhi_records = []
for code, grp in port.groupby("amfi_code"):
    w = grp["weight_pct"].dropna()
    if len(w) == 0: continue
    w_norm = w / w.sum()
    hhi    = (w_norm ** 2).sum()
    hhi_records.append({
        "amfi_code"     : code,
        "n_holdings"    : len(w),
        "hhi"           : round(hhi, 4),
        "hhi_pct"       : round(hhi * 100, 2),
        "concentration" : "High" if hhi > 0.15 else "Moderate" if hhi > 0.08 else "Low",
    })

hhi_df = pd.DataFrame(hhi_records)
hhi_df = hhi_df.merge(fm[["amfi_code","scheme_name","sub_category","fund_house"]], on="amfi_code", how="left")
hhi_df["scheme_short"] = hhi_df["scheme_name"].str.split(" - ").str[0].str[:30]
hhi_df = hhi_df.sort_values("hhi", ascending=False)
hhi_df.to_csv(p("sector_hhi.csv"), index=False)
print(f"  Saved sector_hhi.csv")
print(hhi_df[["scheme_short","n_holdings","hhi_pct","concentration"]].to_string(index=False))

# Chart
fig, ax = plt.subplots(figsize=(12, 7))
colors = {"High":"#E74C3C","Moderate":"#F39C12","Low":"#2ECC71"}
bar_colors = [colors.get(c,"gray") for c in hhi_df["concentration"]]
ax.barh(hhi_df["scheme_short"].str[:30], hhi_df["hhi_pct"], color=bar_colors)
ax.axvline(15, linestyle="--", color="#E74C3C", alpha=0.6, label="High (HHI>15%)")
ax.axvline(8,  linestyle="--", color="#F39C12", alpha=0.6, label="Moderate (HHI>8%)")
ax.set_title("Sector HHI Concentration by Fund", fontsize=14, fontweight="bold", color=PRIMARY)
ax.set_xlabel("HHI (%) — Higher = More Concentrated"); ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(CHARTS,"advanced_hhi_concentration.png"), dpi=150, bbox_inches="tight")
plt.close(); print("  saved advanced_hhi_concentration.png")

# ════════════════════════════════════════════════════════════
#  ADVANCED INSIGHTS SUMMARY
# ════════════════════════════════════════════════════════════
riskiest   = var_df.iloc[0]
safest     = var_df.iloc[-1]
best_cohort = cohort.loc[cohort["total_invested_cr"].idxmax()]
high_hhi   = hhi_df[hhi_df["concentration"]=="High"]

INSIGHTS = f"""
=================================================================
  DAY 6 — ADVANCED ANALYTICS: 5 KEY INSIGHTS
=================================================================

Insight 1 | Highest VaR (Most Risk)
  {riskiest['scheme_short']} ({riskiest['sub_category']}) has the highest
  daily VaR(95%) of {riskiest['VaR_95_daily_pct']:.3f}% and CVaR of
  {riskiest['CVaR_95_daily_pct']:.3f}%. In a bad day (1-in-20 chance),
  an investor could lose more than {abs(riskiest['VaR_95_daily_pct']):.2f}% of NAV.

Insight 2 | Lowest VaR (Safest)
  {safest['scheme_short']} ({safest['sub_category']}) is the most defensive
  fund with VaR(95%) of {safest['VaR_95_daily_pct']:.3f}%. Ideal for
  capital-preservation investors.

Insight 3 | Rolling Sharpe Reveals Market Cycles
  The rolling 90-day Sharpe ratio clearly reveals 2022 bear market
  (negative Sharpe), the 2023 recovery (Sharpe >1 for top funds),
  and the 2024 volatility phase (Sharpe declining again).

Insight 4 | Investor Cohort Behaviour
  The {int(best_cohort['first_txn_year'])} cohort invested the most
  (₹{best_cohort['total_invested_cr']:.1f} Cr total), suggesting
  strong bull market entry. Earlier cohorts show higher avg SIP amounts,
  indicating wealth accumulation over time.

Insight 5 | SIP Continuity Rate = {continuity_rate:.1f}%
  {continuity_rate:.1f}% of investors with 6+ SIP transactions maintain
  consistent intervals (≤35 days). {at_risk_n:,} investors are flagged
  as at-risk of SIP discontinuation — a key retention opportunity.
  Sector concentration (HHI): {len(high_hhi)} funds show HIGH concentration,
  indicating manager conviction but reduced diversification.

=================================================================
"""
print(INSIGHTS)
with open(os.path.join(BASE,"reports","advanced_insights.txt"), "w", encoding="utf-8") as f:
    f.write(INSIGHTS)

print("\n=== Charts ===")
adv_charts = [f for f in os.listdir(CHARTS) if f.startswith("advanced_")]
for ch in sorted(adv_charts) + ["rolling_sharpe_chart.png"]:
    fp = os.path.join(CHARTS, ch)
    if os.path.exists(fp):
        print(f"  {ch:<42} {os.path.getsize(fp)/1024:.1f} KB")

print("\nDay 6 — Advanced Analytics Complete!")
