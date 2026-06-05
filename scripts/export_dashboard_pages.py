"""
Export 4 dashboard page PNGs for submission.
Run: python scripts/export_dashboard_pages.py
"""
import os, warnings
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import matplotlib.ticker as mticker

warnings.filterwarnings("ignore")

BASE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC   = os.path.join(BASE, "data", "processed")
OUT    = os.path.join(BASE, "reports", "charts")
os.makedirs(OUT, exist_ok=True)

PRIMARY   = "#003366"
SECONDARY = "#0077CC"
ACCENT    = "#4DA6FF"

def p(f): return os.path.join(PROC, f)

nav   = pd.read_csv(p("02_nav_history_clean.csv"), parse_dates=["date"])
fm    = pd.read_csv(p("01_fund_master_clean.csv"))
aum   = pd.read_csv(p("03_aum_by_fund_house_clean.csv"), parse_dates=["date"])
sip_m = pd.read_csv(p("04_monthly_sip_inflows_clean.csv"), parse_dates=["month"])
cat_i = pd.read_csv(p("05_category_inflows_clean.csv"), parse_dates=["month"])
folio = pd.read_csv(p("06_industry_folio_count_clean.csv"), parse_dates=["month"])
tx    = pd.read_csv(p("08_investor_transactions_clean.csv"), parse_dates=["transaction_date"])
bench = pd.read_csv(p("10_benchmark_indices_clean.csv"), parse_dates=["date"])
sc    = pd.read_csv(p("fund_scorecard.csv"))
risk  = pd.read_csv(p("fund_risk_metrics.csv"))
nav   = nav.merge(fm[["amfi_code","scheme_name","fund_house"]], on="amfi_code", how="left")
nav["scheme_short"] = nav["scheme_name"].str.split(" - ").str[0].str[:28]

def header_bar(fig, title, subtitle):
    fig.text(0.01, 0.98, "📊 BLUESTOCK MF ANALYTICS", fontsize=9, color="#888",
             transform=fig.transFigure, va="top")
    fig.text(0.5, 0.985, title, ha="center", fontsize=18, fontweight="bold",
             color=PRIMARY, transform=fig.transFigure, va="top")
    fig.text(0.5, 0.965, subtitle, ha="center", fontsize=10, color="#555",
             transform=fig.transFigure, va="top")
    fig.text(0.99, 0.98, "FY 2022–2025", fontsize=9, color="#888",
             ha="right", transform=fig.transFigure, va="top")

def kpi_box(ax, value, label, color=SECONDARY):
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    rect = FancyBboxPatch((0.05,0.1), 0.9, 0.8, boxstyle="round,pad=0.05",
                          facecolor="white", edgecolor=color, linewidth=2)
    ax.add_patch(rect)
    ax.text(0.5, 0.65, value, ha="center", va="center", fontsize=14,
            fontweight="bold", color=PRIMARY)
    ax.text(0.5, 0.28, label, ha="center", va="center", fontsize=7.5, color="#555")

# ─── PAGE 1: Industry Overview ────────────────────────────────
print("[1] Exporting Page1_IndustryOverview.png ...")
fig = plt.figure(figsize=(20,14), facecolor="#F0F4F8")
header_bar(fig, "Industry Overview", "Management snapshot of Indian Mutual Fund Industry")
gs  = gridspec.GridSpec(3, 4, figure=fig, top=0.92, bottom=0.04, hspace=0.4, wspace=0.35)

total_aum   = aum["aum_crore"].sum()/1e5
monthly_sip = sip_m["sip_inflow_crore"].iloc[-1]
total_folio = folio["total_folios_crore"].iloc[-1]

for i,(val,lbl) in enumerate([
    (f"₹{total_aum:.1f}L Cr","Total AUM"),
    (f"₹{monthly_sip:,.0f}Cr","Monthly SIP"),
    (f"{total_folio:.2f} Cr","Total Folios"),
    (f"{fm['amfi_code'].nunique()}","Fund Schemes")]):
    ax = fig.add_subplot(gs[0,i])
    kpi_box(ax, val, lbl)

ax1 = fig.add_subplot(gs[1, :2])
aum_tot = aum.groupby("date")["aum_crore"].sum()
ax1.fill_between(aum_tot.index, aum_tot.values/1e5, alpha=0.3, color=SECONDARY)
ax1.plot(aum_tot.index, aum_tot.values/1e5, color=SECONDARY, linewidth=2)
ax1.set_title("Industry AUM Trend (Lakh Crore)", fontweight="bold", color=PRIMARY)
ax1.set_facecolor("#F8FBFF"); ax1.tick_params(labelsize=8)

ax2 = fig.add_subplot(gs[1, 2:])
aum_fh = aum.groupby("fund_house")["aum_crore"].sum().sort_values().tail(8)
ax2.barh(aum_fh.index, aum_fh.values/1e3, color=SECONDARY)
ax2.set_title("AUM by Fund House (Thousands Crore)", fontweight="bold", color=PRIMARY)
ax2.set_facecolor("#F8FBFF"); ax2.tick_params(labelsize=7)

ax3 = fig.add_subplot(gs[2, :2])
ax3.fill_between(folio["month"], folio["total_folios_crore"], alpha=0.3, color=PRIMARY)
ax3.plot(folio["month"], folio["total_folios_crore"], color=PRIMARY, linewidth=2)
ax3.set_title("Folio Count Growth (Crore)", fontweight="bold", color=PRIMARY)
ax3.set_facecolor("#F8FBFF"); ax3.tick_params(labelsize=8)

ax4 = fig.add_subplot(gs[2, 2:])
cat_latest = cat_i[cat_i["month"]==cat_i["month"].max()].sort_values("net_inflow_crore", ascending=False).head(6)
ax4.bar(cat_latest["category"].str[:12], cat_latest["net_inflow_crore"], color=ACCENT)
ax4.set_title("Latest Month: Net Inflows by Category (Crore)", fontweight="bold", color=PRIMARY)
ax4.set_facecolor("#F8FBFF"); ax4.tick_params(labelsize=7)
plt.setp(ax4.get_xticklabels(), rotation=20, ha="right")

plt.savefig(os.path.join(OUT,"Page1_IndustryOverview.png"), dpi=150, bbox_inches="tight")
plt.close(); print("  saved")

# ─── PAGE 2: Fund Performance ─────────────────────────────────
print("[2] Exporting Page2_FundPerformance.png ...")
fig = plt.figure(figsize=(20,14), facecolor="#F0F4F8")
header_bar(fig, "Fund Performance Analytics", "Risk-adjusted returns · Alpha · Scorecard · Benchmark")
gs = gridspec.GridSpec(3, 4, figure=fig, top=0.92, bottom=0.04, hspace=0.4, wspace=0.35)

for i,(val,lbl) in enumerate([
    (f"{sc['score_100'].max():.0f}/100","Best Score"),
    (f"{risk['sharpe_ratio'].max():.2f}","Best Sharpe"),
    (f"{sc['cagr_3yr'].max():.1f}%","Best 3yr CAGR"),
    (f"{sc['alpha'].max():.1f}%","Best Alpha")]):
    ax = fig.add_subplot(gs[0,i])
    kpi_box(ax, val, lbl)

ax1 = fig.add_subplot(gs[1, :2])
merged = sc.merge(risk[["scheme_short","ann_volatility"]], on="scheme_short", how="left")
ax1.scatter(merged["cagr_3yr"], merged["ann_volatility"],
            c=merged["score_100"], cmap="RdYlGn", s=80, alpha=0.8)
ax1.set_xlabel("3yr CAGR (%)", fontsize=9); ax1.set_ylabel("Annualised Volatility (%)", fontsize=9)
ax1.set_title("Risk vs Return Scatter (bubble=score)", fontweight="bold", color=PRIMARY)
ax1.set_facecolor("#F8FBFF")

ax2 = fig.add_subplot(gs[1, 2:])
top15 = sc.head(15).sort_values("score_100")
colors = ["#2ECC71" if s>=80 else "#F1C40F" if s>=60 else "#E74C3C" for s in top15["score_100"]]
ax2.barh(top15["scheme_short"].str[:25], top15["score_100"], color=colors)
ax2.set_title("Fund Scorecard — Top 15 (0–100)", fontweight="bold", color=PRIMARY)
ax2.set_facecolor("#F8FBFF"); ax2.tick_params(labelsize=7)

ax3 = fig.add_subplot(gs[2, :])
start = pd.Timestamp("2022-01-03")
pal = [SECONDARY, ACCENT, "#E74C3C", "#2ECC71", "#F39C12"]
top5 = sc.head(5)["scheme_short"].tolist()
for i, name in enumerate(top5):
    grp = nav[nav["scheme_short"]==name].sort_values("date")
    grp = grp[grp["date"]>=start]
    if len(grp)<2: continue
    ax3.plot(grp["date"], grp["nav"]/grp["nav"].iloc[0]*100,
             linewidth=1.8, color=pal[i], label=name[:25], alpha=0.85)
nifty50 = bench[bench["index_name"]=="NIFTY50"].set_index("date")["close_value"]
n50 = nifty50[nifty50.index>=start]
ax3.plot(n50.index, n50/n50.iloc[0]*100, linewidth=2.5, linestyle="--", color="black", label="NIFTY50")
ax3.set_title("Top 5 Funds vs NIFTY50 (Base=100)", fontweight="bold", color=PRIMARY)
ax3.legend(fontsize=7, ncol=3); ax3.set_facecolor("#F8FBFF")

plt.savefig(os.path.join(OUT,"Page2_FundPerformance.png"), dpi=150, bbox_inches="tight")
plt.close(); print("  saved")

# ─── PAGE 3: Investor Analytics ───────────────────────────────
print("[3] Exporting Page3_InvestorAnalytics.png ...")
fig = plt.figure(figsize=(20,14), facecolor="#F0F4F8")
header_bar(fig, "Investor Analytics", "Demographics · Geography · Transaction Patterns")
gs = gridspec.GridSpec(3, 4, figure=fig, top=0.92, bottom=0.04, hspace=0.4, wspace=0.35)

for i,(val,lbl) in enumerate([
    (f"₹{tx['amount_inr'].sum()/1e7:,.0f}Cr","Total Invested"),
    (f"{len(tx):,}","Transactions"),
    (f"₹{tx['amount_inr'].mean():,.0f}","Avg Ticket"),
    (f"{tx['state'].nunique()}","States Active")]):
    ax = fig.add_subplot(gs[0,i])
    kpi_box(ax, val, lbl)

ax1 = fig.add_subplot(gs[1, :2])
state_amt = tx.groupby("state")["amount_inr"].sum().sort_values(ascending=True)/1e7
ax1.barh(state_amt.index, state_amt.values, color=SECONDARY)
ax1.set_title("Transaction Amount by State (Crore)", fontweight="bold", color=PRIMARY)
ax1.set_facecolor("#F8FBFF"); ax1.tick_params(labelsize=7)

ax2 = fig.add_subplot(gs[1, 2])
tt = tx["transaction_type"].value_counts()
ax2.pie(tt, labels=tt.index, autopct="%1.0f%%",
        colors=[SECONDARY, ACCENT, "#E74C3C"], startangle=90)
ax2.set_title("Transaction\nType Split", fontweight="bold", color=PRIMARY, fontsize=9)

ax3 = fig.add_subplot(gs[1, 3])
gen = tx["gender"].value_counts()
ax3.pie(gen, labels=gen.index, autopct="%1.0f%%",
        colors=["#AED6F1","#F9A7B0"], startangle=90)
ax3.set_title("Gender\nSplit", fontweight="bold", color=PRIMARY, fontsize=9)

ax4 = fig.add_subplot(gs[2, :2])
age_order = [a for a in ["18-25","26-35","36-45","46-55","56+"] if a in tx["age_group"].unique()]
age_avg = tx.groupby("age_group")["amount_inr"].mean().reindex(age_order)
ax4.bar(age_avg.index, age_avg.values, color=[SECONDARY,ACCENT,PRIMARY,SECONDARY,ACCENT][:len(age_avg)])
ax4.set_title("Avg SIP Amount by Age Group (INR)", fontweight="bold", color=PRIMARY)
ax4.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"₹{x/1e3:.0f}K"))
ax4.set_facecolor("#F8FBFF"); ax4.tick_params(labelsize=8)

ax5 = fig.add_subplot(gs[2, 2:])
tx2 = tx.copy()
tx2["month"] = tx2["transaction_date"].dt.to_period("M").dt.to_timestamp()
mv = tx2.groupby(["month","transaction_type"])["amount_inr"].sum().unstack(fill_value=0)/1e7
for col, col_color in zip(mv.columns, [SECONDARY, ACCENT, "#E74C3C"]):
    ax5.plot(mv.index, mv[col], label=col, linewidth=2, color=col_color)
ax5.set_title("Monthly Transaction Volume (Crore)", fontweight="bold", color=PRIMARY)
ax5.legend(fontsize=8); ax5.set_facecolor("#F8FBFF"); ax5.tick_params(labelsize=8)

plt.savefig(os.path.join(OUT,"Page3_InvestorAnalytics.png"), dpi=150, bbox_inches="tight")
plt.close(); print("  saved")

# ─── PAGE 4: SIP & Market Trends ─────────────────────────────
print("[4] Exporting Page4_SIPMarketTrends.png ...")
fig = plt.figure(figsize=(20,14), facecolor="#F0F4F8")
header_bar(fig, "SIP & Market Trends", "SIP flows · Category rotation · Market correlation")
gs = gridspec.GridSpec(3, 4, figure=fig, top=0.92, bottom=0.04, hspace=0.4, wspace=0.35)

for i,(val,lbl) in enumerate([
    (f"₹{sip_m['sip_inflow_crore'].sum():,.0f}Cr","Total SIP Inflows"),
    (f"₹{sip_m['sip_inflow_crore'].max():,.0f}Cr","Peak Monthly SIP"),
    (f"₹{sip_m['sip_inflow_crore'].mean():,.0f}Cr","Avg Monthly SIP"),
    (f"{sip_m['sip_inflow_crore'].pct_change().mean()*100:.1f}%","Avg Monthly Growth")]):
    ax = fig.add_subplot(gs[0,i])
    kpi_box(ax, val, lbl)

ax1 = fig.add_subplot(gs[1, :])
ax1r = ax1.twinx()
ax1.bar(sip_m["month"], sip_m["sip_inflow_crore"], color=SECONDARY, alpha=0.7, label="SIP Inflows (Crore)")
nifty50_m = bench[bench["index_name"]=="NIFTY50"].set_index("date")["close_value"].resample("MS").last()
common = sip_m.set_index("month").index.intersection(nifty50_m.index)
if len(common)>0:
    ax1r.plot(nifty50_m[common].index, nifty50_m[common].values,
              color="#E74C3C", linewidth=2.5, label="NIFTY50")
ax1.set_title("Monthly SIP Inflows vs NIFTY50 (Dual Axis)", fontweight="bold", color=PRIMARY)
ax1.set_facecolor("#F8FBFF")
ax1.legend(loc="upper left", fontsize=8); ax1r.legend(loc="upper right", fontsize=8)

ax2 = fig.add_subplot(gs[2, :2])
cat_i["month_str"] = cat_i["month"].dt.strftime("%b-%y")
pivot = cat_i.pivot_table(values="net_inflow_crore", index="category", columns="month_str", aggfunc="sum")
import seaborn as sns
sns.heatmap(pivot, cmap="RdYlGn", center=0, linewidths=0.3, ax=ax2,
            annot=False, cbar_kws={"shrink":0.7})
ax2.set_title("Category Inflow Heatmap", fontweight="bold", color=PRIMARY)
ax2.tick_params(axis="x", labelsize=6, rotation=45)
ax2.tick_params(axis="y", labelsize=7)

ax3 = fig.add_subplot(gs[2, 2:])
latest_cat = cat_i[cat_i["month"]==cat_i["month"].max()].sort_values("net_inflow_crore", ascending=False).head(7)
colors = [SECONDARY if v>0 else "#E74C3C" for v in latest_cat["net_inflow_crore"]]
ax3.barh(latest_cat["category"].str[:18], latest_cat["net_inflow_crore"], color=colors)
ax3.set_title("Top Categories — Latest Month", fontweight="bold", color=PRIMARY)
ax3.set_facecolor("#F8FBFF"); ax3.tick_params(labelsize=8)

plt.savefig(os.path.join(OUT,"Page4_SIPMarketTrends.png"), dpi=150, bbox_inches="tight")
plt.close(); print("  saved")

print("\n✅ All 4 dashboard pages exported to reports/charts/")
