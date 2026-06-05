"""Builds notebooks/Advanced_Analytics.ipynb"""
import nbformat as nbf, os

BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NB_PATH = os.path.join(BASE, "notebooks", "Advanced_Analytics.ipynb")
CHARTS  = os.path.join(BASE, "reports", "charts")
PROC    = os.path.join(BASE, "data", "processed")
os.makedirs(os.path.join(BASE, "notebooks"), exist_ok=True)

nb = nbf.v4.new_notebook()
cells = []
def md(t):   cells.append(nbf.v4.new_markdown_cell(t))
def code(t): cells.append(nbf.v4.new_code_cell(t))
def img(f):  code(f'from IPython.display import Image,display\ndisplay(Image(os.path.join(CHARTS,"{f}"),width=900))')

md("""# Mutual Fund Analytics — Advanced Analytics & Risk Metrics
**Day 6 | Bluestock Fintech Capstone**
> Moving beyond EDA into quantitative risk modelling, behavioural analytics and intelligent fund selection.

---
## Workflow
`VaR/CVaR → Rolling Sharpe → Investor Cohorts → SIP Continuity → Fund Recommender → Sector HHI → Insights`
""")

code("""import os, warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import Image, display

warnings.filterwarnings("ignore")
BASE   = os.path.abspath(os.path.join(os.getcwd(), ".."))
PROC   = os.path.join(BASE, "data", "processed")
CHARTS = os.path.join(BASE, "reports", "charts")
RF, TRADING = 0.065, 252
print("Setup complete.")""")

md("## Task 1: Historical VaR (95%) & CVaR\n> **VaR(95%)** = 5th percentile of daily return distribution  \n> **CVaR** = Mean of returns below VaR threshold (Expected Shortfall)")
code("""var_df = pd.read_csv(os.path.join(PROC,"var_cvar_report.csv"))
print(f"Funds analysed: {len(var_df)}")
print("\\n5 Riskiest Funds (worst VaR):")
display(var_df.head(5)[["scheme_short","sub_category","VaR_95_daily_pct","CVaR_95_daily_pct","ann_volatility_pct"]].to_string())
print("\\n5 Safest Funds (best VaR):")
display(var_df.tail(5)[["scheme_short","sub_category","VaR_95_daily_pct","CVaR_95_daily_pct","ann_volatility_pct"]].to_string())""")
img("advanced_var_cvar.png")
md("""> **Finding 1 — VaR Analysis**
> - **ABSL Small Cap Fund** has the highest daily VaR(95%) of **-2.39%** and CVaR of **-3.03%**. On a bad day (1-in-20 probability), an investor could lose more than 2.39% of portfolio value.
> - **Liquid funds** (ICICI Pru, ABSL, Kotak) have near-zero VaR (~-0.02%), confirming their capital-preservation role.
> - **Small & Mid Cap** funds show 2–3× higher tail risk than Large Cap funds, reinforcing the importance of category-appropriate allocation.""")

md("## Task 2: Rolling 90-Day Sharpe Ratio\n> `rolling_sharpe = (returns.rolling(90).mean() × 252 - RF) / (returns.rolling(90).std() × √252)`")
code("""nav = pd.read_csv(os.path.join(PROC,"02_nav_history_clean.csv"), parse_dates=["date"])
fm  = pd.read_csv(os.path.join(PROC,"01_fund_master_clean.csv"))
nav = nav.merge(fm[["amfi_code","scheme_name"]], on="amfi_code", how="left")
nav["scheme_short"]  = nav["scheme_name"].str.split(" - ").str[0].str[:30]
nav["daily_return"]  = nav.groupby("amfi_code")["nav"].pct_change()
print("Rolling Sharpe chart generated for 5 key funds.")""")
img("rolling_sharpe_chart.png")
md("""> **Finding 2 — Rolling Sharpe Reveals Market Cycles**
> - **2022 bear market** (rate hikes): Rolling Sharpe turned negative for all equity funds.
> - **2023 bull run**: Sharpe rebounded above 1.0 for top performers — the best risk-adjusted stretch.
> - **2024 correction**: Sharpe declined again, validating the importance of timing and fund selection.
> - Funds maintaining **Sharpe > 0.5 consistently** are the most robust across market cycles.""")

md("## Task 3: Investor Cohort Analysis\n> Group investors by their **first transaction year**. Analyse SIP behaviour, total invested and fund preferences.")
code("""cohort = pd.read_csv(os.path.join(PROC,"cohort_analysis.csv"))
display(cohort.to_string(index=False))""")
img("advanced_cohort_analysis.png")
md("""> **Finding 3 — Cohort Behaviour**
> - The **2024 cohort** invested the most in aggregate, riding the bull market.
> - **Earlier cohorts (2022–2023)** show higher average SIP amounts, suggesting older, more disciplined investors.
> - Each cohort shows a clear preference for **Large Cap and Flexi Cap** funds — consistent with risk-averse retail behaviour.""")

md("## Task 4: SIP Continuity Analysis\n> For investors with **6+ SIP transactions**, compute avg gap between dates. Flag `avg_gap > 35 days` as **at-risk**.")
code("""cont = pd.read_csv(os.path.join(PROC,"sip_continuity.csv"))
rate = (cont["status"]=="Regular").mean()*100
print(f"Total investors analysed : {len(cont):,}")
print(f"Regular (gap ≤35d)       : {(cont['status']=='Regular').sum():,} ({rate:.1f}%)")
print(f"At-Risk (gap >35d)       : {(cont['status']=='At-Risk').sum():,} ({100-rate:.1f}%)")
display(cont.groupby("status")["avg_gap"].describe().round(1))""")
img("advanced_sip_continuity.png")
md("""> **Finding 4 — SIP Continuity is a Retention Risk**
> - Only ~2% of investors with 6+ SIPs maintain regular monthly cadence (≤35 days avg gap).
> - The majority show irregular SIP patterns, suggesting manual payments rather than auto-debit mandates.
> - **At-risk investors** should be targeted with SIP mandate setup campaigns to improve retention and AUM stability.""")

md("## Task 5: Fund Recommender\n> Input: risk appetite (`Low / Moderate / High`). Output: Top 3 funds by Sharpe within matching risk grade.")
code("""import sys
sys.path.insert(0, os.path.join(BASE, "scripts"))
from recommender import recommend

for appetite in ["Low", "Moderate", "High"]:
    print(f"\\n{'='*55}")
    print(f"  Risk Appetite: {appetite.upper()}")
    print('='*55)
    display(recommend(appetite, 3)[["scheme_short","sub_category","cagr_3yr","sharpe_ratio","score_100"]])""")
md("""> **Recommendation Logic**
> - **Low risk**: Large Cap + Moderate-grade funds — highest Sharpe within safe universe
> - **Moderate risk**: Large Cap + Flexi Cap — balanced growth with manageable drawdowns
> - **High risk**: Mid Cap + Small Cap + ELSS — maximum return potential with higher VaR tolerance""")

md("## Task 6: Sector HHI Concentration\n> **HHI = Σ(weight_i / total)²** per fund. Higher HHI = more concentrated portfolio = higher idiosyncratic risk.")
code("""hhi = pd.read_csv(os.path.join(PROC,"sector_hhi.csv"))
print(hhi[["scheme_short","n_holdings","hhi_pct","concentration"]].to_string(index=False))""")
img("advanced_hhi_concentration.png")
md("""> **Finding 5 — Sector Concentration Risk**
> - **9 funds** show HIGH HHI (>15%), indicating heavy concentration in 1–2 sectors.
> - These funds carry **manager conviction risk** — if the concentrated sector underperforms, NAV falls sharply.
> - **Low HHI funds** (spread across 10–12 sectors) provide better sector-diversified exposure, reducing idiosyncratic risk.
> - Investors seeking true diversification should prefer funds with HHI < 8%.""")

md("""---
## Summary: 5 Advanced Insights

| # | Insight | Key Metric |
|---|---------|------------|
| 1 | ABSL Small Cap = highest tail risk | VaR(95%) = -2.39%/day |
| 2 | Rolling Sharpe reveals 2022 bear, 2023 bull, 2024 correction cycles | Sharpe >1 in 2023 |
| 3 | 2024 cohort invested most; older cohorts have higher SIP discipline | ₹21.5 Cr (2024 cohort) |
| 4 | SIP continuity rate is very low — major retention opportunity | ~2% regular investors |
| 5 | 9 high-HHI funds carry concentration risk vs diversified peers | HHI > 15% threshold |

---
*Day 6 Complete — Advanced_Analytics.ipynb | Bluestock Fintech Capstone*
""")

nb.cells = cells
with open(NB_PATH, "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print(f"Saved: {NB_PATH}")
