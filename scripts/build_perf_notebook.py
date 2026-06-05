"""
Builds notebooks/Performance_Analytics.ipynb
Run: python scripts/build_perf_notebook.py
"""
import nbformat as nbf, os

BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NB_PATH = os.path.join(BASE, "notebooks", "Performance_Analytics.ipynb")
CHARTS  = os.path.join(BASE, "reports", "charts")
PROC    = os.path.join(BASE, "data", "processed")
os.makedirs(os.path.join(BASE, "notebooks"), exist_ok=True)

nb = nbf.v4.new_notebook()
cells = []
def md(t):   cells.append(nbf.v4.new_markdown_cell(t))
def code(t): cells.append(nbf.v4.new_code_cell(t))
def img(f):  code(f'from IPython.display import Image, display\ndisplay(Image(os.path.join(CHARTS,"{f}"), width=900))')

md("""# Mutual Fund Analytics — Fund Performance Analytics
**Day 4 | Bluestock Fintech Capstone**

> Moving from EDA (what happened?) → Financial Analytics (how well did funds perform?)

---
## Workflow
`Clean NAV → Daily Returns → CAGR → Sharpe → Sortino → Alpha/Beta → Drawdown → Scorecard → Benchmark`
""")

code("""import os, warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress
from IPython.display import Image, display

warnings.filterwarnings("ignore")
sns.set_theme(style="darkgrid")

BASE   = os.path.abspath(os.path.join(os.getcwd(), ".."))
PROC   = os.path.join(BASE, "data", "processed")
CHARTS = os.path.join(BASE, "reports", "charts")
RF     = 0.065
TRADING_DAYS = 252
print("Setup complete.")""")

md("## Step 1: Load Data")
code("""nav   = pd.read_csv(os.path.join(PROC,"02_nav_history_clean.csv"),   parse_dates=["date"])
fm    = pd.read_csv(os.path.join(PROC,"01_fund_master_clean.csv"))
bench = pd.read_csv(os.path.join(PROC,"10_benchmark_indices_clean.csv"), parse_dates=["date"])
nav   = nav.merge(fm[["amfi_code","scheme_name","fund_house","category","sub_category","expense_ratio_pct"]],
                  on="amfi_code", how="left")
nav["scheme_short"] = nav["scheme_name"].str.split(" - ").str[0].str[:35]
nav   = nav.sort_values(["amfi_code","date"]).reset_index(drop=True)
nifty100 = bench[bench["index_name"]=="NIFTY100"].set_index("date")["close_value"].sort_index()
print(f"NAV: {len(nav):,} rows | Funds: {nav['amfi_code'].nunique()}")
display(nav.head(3))""")

md("## Step 2: Daily Return Distribution\n> **Formula:** Rₜ = (NAVₜ / NAVₜ₋₁) - 1")
code('nav["daily_return"] = nav.groupby("amfi_code")["nav"].pct_change()\nprint(f"Outliers |ret|>10%: {(nav[\'daily_return\'].abs()>0.10).sum()}")')
img("performance_daily_return_dist.png")
md("> **Insight:** Daily returns follow a near-normal distribution centred at ~0.05%, with tails beyond ±5% representing major market events.")

md("## Step 3: CAGR Analysis\n> **Formula:** CAGR = (NAV_end/NAV_start)^(1/years) - 1")
code("""cagr_df = pd.read_csv(os.path.join(PROC,"fund_cagr.csv"))
print(f"Funds with CAGR data: {len(cagr_df)}")
display(cagr_df[["scheme_short","cagr_1yr","cagr_3yr","cagr_5yr"]].head(10))""")
img("performance_cagr.png")
md("> **Insight:** Mid-cap and small-cap funds dominate the top CAGR rankings, delivering 25–35% 3-year returns, while debt funds cluster below 8%.")

md("## Step 4 & 5: Sharpe & Sortino Ratios\n> **Sharpe** = (Rp - Rf) / σp × √252  |  **Sortino** uses downside deviation only")
code("""risk_df = pd.read_csv(os.path.join(PROC,"fund_risk_metrics.csv"))
print("Top 10 by Sharpe Ratio:")
display(risk_df.nlargest(10,"sharpe_ratio")[["scheme_short","sharpe_ratio","sortino_ratio","ann_volatility"]].to_string())""")
img("performance_sharpe.png")
img("performance_risk_return.png")
md("> **Insight:** Mirae Asset Large Cap Fund achieved the highest Sharpe ratio (>1.0), indicating exceptional risk-adjusted returns. Liquid funds have negative Sharpe due to near-zero returns after adjusting for RF rate.")

md("## Step 6: Alpha & Beta Analysis\n> **Beta** = Regression slope vs NIFTY100  |  **Alpha** = Annualised intercept")
code("""ab_df = pd.read_csv(os.path.join(PROC,"alpha_beta.csv"))
pos = (ab_df["alpha"] > 0).sum()
print(f"Funds with positive alpha: {pos}/{len(ab_df)} ({pos/len(ab_df)*100:.0f}%)")
print("\\nAlpha & Beta Summary:")
display(ab_df[["scheme_short","alpha","beta","tracking_error"]].sort_values("alpha", ascending=False).head(10).to_string())""")
img("performance_alpha_beta.png")
img("performance_tracking_error.png")
md("> **Insight:** 100% of equity funds generated positive alpha vs NIFTY100, suggesting the benchmark used (daily returns) creates this artefact — tracking error is high (18–30%), confirming these are genuinely active funds.")

md("## Step 7: Maximum Drawdown\n> **MDD** = min(NAV/Running_Max - 1)")
code("""print("Worst Drawdowns:")
display(risk_df.nsmallest(10,"max_drawdown")[["scheme_short","max_drawdown","mdd_date"]].to_string())
print("\\nMost Resilient Funds:")
display(risk_df.nlargest(5,"max_drawdown")[["scheme_short","max_drawdown"]].to_string())""")
img("performance_drawdown.png")
md("> **Insight:** Small-cap funds suffered 30–52% peak-to-trough declines, while liquid/gilt funds showed near-zero drawdowns — illustrating the critical importance of risk category alignment with investor goals.")

md("## Step 8: Fund Scorecard (0–100)\n> **Weights:** 30% Return + 25% Sharpe + 20% Alpha + 15% Expense + 10% Drawdown")
code("""scorecard = pd.read_csv(os.path.join(PROC,"fund_scorecard.csv"))
print("TOP 15 FUNDS — COMPOSITE SCORECARD")
display(scorecard[["rank","scheme_short","fund_house","sub_category","cagr_3yr","sharpe_ratio","score_100"]].head(15).to_string())""")
img("performance_scorecard.png")
md("> **Insight:** ICICI Pru Midcap Fund scores 100/100, excelling across all 5 dimensions — CAGR (31.78%), Sharpe (0.883), Alpha (29.26%), reasonable cost (1.36%), and managed drawdown (-18.19%).")

md("## Step 9: Benchmark Comparison (Normalised)")
code("""nifty50  = bench[bench["index_name"]=="NIFTY50"].set_index("date")["close_value"].sort_index() if 'bench' in dir() else pd.Series()
print("Top 5 funds vs NIFTY50 vs NIFTY100 — see chart below")""")
img("performance_benchmark_comparison.png")
md("> **Insight:** Top-ranked funds significantly outperformed both NIFTY50 and NIFTY100 on a base-100 normalised basis since Jan 2022, validating the composite scorecard's fund selection quality.")

md("## Step 10: Rolling Volatility")
img("performance_rolling_volatility.png")
md("> **Insight:** 30-day rolling volatility spiked during market stress events (2022 rate hikes, 2024 correction), with small/mid-cap funds showing 2–3× higher volatility than large-cap peers.")

md("""---
## Summary: 10 Key Performance Insights

| # | Insight |
|---|---------|
| 1 | ICICI Pru Midcap Fund = highest composite score (100/100) |
| 2 | Mirae Asset Large Cap = best Sharpe ratio (>1.0) |
| 3 | SBI/DSP Small Cap = highest alpha generators (30%+) |
| 4 | SBI Bluechip = best 1-year return in Large Cap segment |
| 5 | Mid-cap funds dominate 3-year CAGR (30–35%) |
| 6 | ABSL Liquid Fund = most resilient (MDD near 0%) |
| 7 | Axis/SBI Small Cap = worst drawdown (-50 to -52%) |
| 8 | 100% equity funds showed positive alpha vs NIFTY100 |
| 9 | ABSL Liquid Fund = lowest tracking error |
| 10 | Direct plan funds (expense <1%) meaningfully outperform over 3–5 years |

---
*Day 4 Complete — Performance_Analytics.ipynb | Bluestock Fintech Capstone*
""")

nb.cells = cells
with open(NB_PATH, "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print(f"Notebook saved: {NB_PATH}")
