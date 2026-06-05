"""
Bluestock MF Dashboard — Day 5
Run: streamlit run dashboard/app.py
"""
import os, sys
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ── Paths ──────────────────────────────────────────────────
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(BASE, "data", "processed")

def p(f): return os.path.join(PROC, f)

# ── Theme ───────────────────────────────────────────────────
PRIMARY   = "#003366"
SECONDARY = "#0077CC"
ACCENT    = "#4DA6FF"
BG        = "#F0F4F8"
WHITE     = "#FFFFFF"

st.set_page_config(
    page_title="Bluestock MF Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(f"""
<style>
  .main {{ background:{BG}; }}
  [data-testid="stSidebar"] {{ background:{PRIMARY}; }}
  [data-testid="stSidebar"] * {{ color:{WHITE} !important; }}
  .metric-card {{
    background:{WHITE}; border-radius:12px; padding:18px 22px;
    box-shadow:0 2px 8px rgba(0,0,0,.10); border-left:5px solid {SECONDARY};
  }}
  .metric-val {{ font-size:2rem; font-weight:700; color:{PRIMARY}; }}
  .metric-lbl {{ font-size:.82rem; color:#555; margin-top:2px; }}
  h1,h2,h3 {{ color:{PRIMARY}; }}
  .page-header {{
    background:linear-gradient(90deg,{PRIMARY},{SECONDARY});
    color:{WHITE}; padding:18px 28px; border-radius:10px;
    margin-bottom:18px;
  }}
</style>
""", unsafe_allow_html=True)

# ── Load Data ───────────────────────────────────────────────
@st.cache_data
def load():
    nav   = pd.read_csv(p("02_nav_history_clean.csv"),   parse_dates=["date"])
    fm    = pd.read_csv(p("01_fund_master_clean.csv"))
    aum   = pd.read_csv(p("03_aum_by_fund_house_clean.csv"), parse_dates=["date"])
    sip_m = pd.read_csv(p("04_monthly_sip_inflows_clean.csv"), parse_dates=["month"])
    cat_i = pd.read_csv(p("05_category_inflows_clean.csv"), parse_dates=["month"])
    folio = pd.read_csv(p("06_industry_folio_count_clean.csv"), parse_dates=["month"])
    perf  = pd.read_csv(p("07_scheme_performance_clean.csv"))
    tx    = pd.read_csv(p("08_investor_transactions_clean.csv"), parse_dates=["transaction_date"])
    port  = pd.read_csv(p("09_portfolio_holdings_clean.csv"))
    bench = pd.read_csv(p("10_benchmark_indices_clean.csv"), parse_dates=["date"])
    sc    = pd.read_csv(p("fund_scorecard.csv"))
    ab    = pd.read_csv(p("alpha_beta.csv"))
    risk  = pd.read_csv(p("fund_risk_metrics.csv"))
    nav   = nav.merge(fm[["amfi_code","scheme_name","fund_house","category",
                           "sub_category","expense_ratio_pct"]], on="amfi_code", how="left")
    nav["scheme_short"] = nav["scheme_name"].str.split(" - ").str[0].str[:30]
    return nav, fm, aum, sip_m, cat_i, folio, perf, tx, port, bench, sc, ab, risk

nav, fm, aum, sip_m, cat_i, folio, perf, tx, port, bench, sc, ab, risk = load()

def blueplot(fig, h=420):
    fig.update_layout(
        plot_bgcolor=WHITE, paper_bgcolor=WHITE,
        font=dict(family="Inter, Arial", color=PRIMARY),
        height=h, margin=dict(l=20,r=20,t=40,b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        colorway=[SECONDARY, ACCENT, "#E74C3C", "#2ECC71", "#F39C12",
                  "#9B59B6", "#1ABC9C", "#E67E22"],
    )
    return fig

def kpi(col, value, label, delta=None):
    d = f"<span style='font-size:.8rem;color:#27AE60'>▲ {delta}</span>" if delta else ""
    col.markdown(f"""
    <div class='metric-card'>
      <div class='metric-val'>{value}</div>
      <div class='metric-lbl'>{label} {d}</div>
    </div>""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Bluestock MF")
    st.markdown("**Analytics Dashboard**")
    st.markdown("---")
    page = st.radio("Navigate", [
        "🏭 Industry Overview",
        "📈 Fund Performance",
        "👥 Investor Analytics",
        "💰 SIP & Market Trends",
    ])
    st.markdown("---")
    st.markdown("**Data:** FY 2022–2025")
    st.markdown("**Funds:** 40 schemes")
    st.markdown("**Source:** Bluestock Fintech")

# ════════════════════════════════════════════════════════════
# PAGE 1 — INDUSTRY OVERVIEW
# ════════════════════════════════════════════════════════════
if page == "🏭 Industry Overview":
    st.markdown("<div class='page-header'><h2 style='color:white;margin:0'>🏭 Industry Overview</h2><p style='color:#cce;margin:0'>Management snapshot of Indian Mutual Fund Industry</p></div>", unsafe_allow_html=True)

    total_aum   = aum["aum_crore"].sum() / 1e5
    monthly_sip = sip_m["sip_inflow_crore"].iloc[-1]
    total_folio = folio["total_folios_crore"].iloc[-1]
    schemes     = fm["amfi_code"].nunique()

    c1,c2,c3,c4 = st.columns(4)
    kpi(c1, f"₹{total_aum:.1f}L Cr", "Total Industry AUM", "+18% YoY")
    kpi(c2, f"₹{monthly_sip:,.0f} Cr", "Latest Monthly SIP")
    kpi(c3, f"{total_folio:.2f} Cr", "Total Folios")
    kpi(c4, str(schemes), "Fund Schemes")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([3,2])
    with col1:
        st.subheader("📈 Industry AUM Trend (2022–2025)")
        aum_total = aum.groupby("date")["aum_crore"].sum().reset_index()
        fig = px.area(aum_total, x="date", y="aum_crore",
                      title="", labels={"aum_crore":"AUM (Crore)","date":"Date"})
        fig.update_traces(line_color=SECONDARY, fillcolor=f"rgba(0,119,204,0.15)")
        st.plotly_chart(blueplot(fig), use_container_width=True)

    with col2:
        st.subheader("🏦 AUM by Fund House")
        aum_fh = aum.groupby("fund_house")["aum_crore"].sum().sort_values(ascending=True).tail(10)
        fig = px.bar(aum_fh.reset_index(), x="aum_crore", y="fund_house",
                     orientation="h", labels={"aum_crore":"AUM (Crore)","fund_house":""})
        fig.update_traces(marker_color=SECONDARY)
        st.plotly_chart(blueplot(fig), use_container_width=True)

    col3, col4 = st.columns([2,3])
    with col3:
        st.subheader("🗺️ Market Share Treemap")
        aum_fh2 = aum.groupby("fund_house")["aum_crore"].sum().reset_index()
        fig = px.treemap(aum_fh2, path=["fund_house"], values="aum_crore",
                         color="aum_crore", color_continuous_scale=[[0,"#AED6F1"],[1,PRIMARY]])
        st.plotly_chart(blueplot(fig, 380), use_container_width=True)

    with col4:
        st.subheader("📊 Category-wise Folio Distribution")
        cat_i["month_str"] = cat_i["month"].dt.strftime("%Y-%m")
        cat_latest = cat_i[cat_i["month"] == cat_i["month"].max()]
        fig = px.bar(cat_latest.sort_values("net_inflow_crore",ascending=False),
                     x="category", y="net_inflow_crore",
                     labels={"net_inflow_crore":"Net Inflow (Cr)","category":"Category"})
        fig.update_traces(marker_color=ACCENT)
        st.plotly_chart(blueplot(fig, 380), use_container_width=True)

# ════════════════════════════════════════════════════════════
# PAGE 2 — FUND PERFORMANCE
# ════════════════════════════════════════════════════════════
elif page == "📈 Fund Performance":
    st.markdown("<div class='page-header'><h2 style='color:white;margin:0'>📈 Fund Performance Analytics</h2><p style='color:#cce;margin:0'>Risk-adjusted returns, alpha, scorecard & benchmark comparison</p></div>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### Filters")
        fh_opts  = ["All"] + sorted(sc["fund_house"].dropna().unique().tolist())
        cat_opts = ["All"] + sorted(sc["sub_category"].dropna().unique().tolist())
        sel_fh   = st.selectbox("Fund House", fh_opts)
        sel_cat  = st.selectbox("Sub-Category", cat_opts)

    df = sc.copy()
    if sel_fh  != "All": df = df[df["fund_house"] == sel_fh]
    if sel_cat != "All": df = df[df["sub_category"] == sel_cat]

    c1,c2,c3,c4 = st.columns(4)
    kpi(c1, f"{df['score_100'].max():.1f}", "Best Composite Score")
    kpi(c2, f"{df['sharpe_ratio'].max():.2f}", "Best Sharpe Ratio")
    kpi(c3, f"{df['cagr_3yr'].max():.1f}%", "Best 3yr CAGR")
    kpi(c4, f"{df['alpha'].max():.1f}%", "Best Alpha")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([3,2])
    with col1:
        st.subheader("🎯 Risk vs Return Scatter")
        sc_full = sc.merge(risk[["amfi_code","ann_volatility"]], on="amfi_code", how="left") if "amfi_code" in sc.columns else sc
        merged = df.merge(risk[["scheme_short","ann_volatility","max_drawdown"]], on="scheme_short", how="left")
        fig = px.scatter(merged, x="cagr_3yr", y="ann_volatility",
                         size="score_100", color="sub_category",
                         hover_name="scheme_short",
                         hover_data={"sharpe_ratio":True,"alpha":True},
                         labels={"cagr_3yr":"3yr CAGR (%)","ann_volatility":"Volatility (%)"})
        st.plotly_chart(blueplot(fig), use_container_width=True)

    with col2:
        st.subheader("🏆 Top 10 Scorecard")
        cols_show = ["rank","scheme_short","cagr_3yr","sharpe_ratio","score_100"]
        display_df = df[cols_show].head(10).copy()
        display_df.columns = ["Rank","Fund","3yr CAGR","Sharpe","Score"]
        st.dataframe(display_df.set_index("Rank"), use_container_width=True, height=380)

    st.subheader("📉 Benchmark Comparison — Top 5 Funds vs NIFTY50 / NIFTY100")
    top5_names = sc.head(5)["scheme_short"].tolist()
    nifty50  = bench[bench["index_name"]=="NIFTY50" ].set_index("date")["close_value"]
    nifty100 = bench[bench["index_name"]=="NIFTY100"].set_index("date")["close_value"]
    fig = go.Figure()
    start = pd.Timestamp("2022-01-03")
    pal = [SECONDARY, ACCENT, "#E74C3C", "#2ECC71", "#F39C12"]
    for i, name in enumerate(top5_names):
        grp = nav[nav["scheme_short"]==name].sort_values("date")
        grp = grp[grp["date"]>=start]
        if len(grp)<2: continue
        fig.add_trace(go.Scatter(x=grp["date"], y=grp["nav"]/grp["nav"].iloc[0]*100,
                                 name=name[:28], line=dict(color=pal[i], width=1.8)))
    for bm, ser, col in [("NIFTY50",nifty50,"black"),("NIFTY100",nifty100,"dimgray")]:
        s = ser[ser.index>=start].dropna()
        fig.add_trace(go.Scatter(x=s.index, y=s/s.iloc[0]*100, name=bm,
                                 line=dict(color=col, width=2.5, dash="dash")))
    fig.update_layout(title="Normalised Performance (Base=100)",
                      yaxis_title="Value (Base 100)", xaxis_title="Date")
    st.plotly_chart(blueplot(fig, 440), use_container_width=True)

    st.subheader("📋 Full Fund Scorecard")
    st.dataframe(df[["rank","scheme_short","fund_house","sub_category",
                      "cagr_3yr","sharpe_ratio","alpha","max_drawdown","expense_ratio_pct","score_100"]]
                  .rename(columns={"scheme_short":"Fund","fund_house":"AMC","sub_category":"Category",
                                   "cagr_3yr":"3yr CAGR%","sharpe_ratio":"Sharpe","alpha":"Alpha%",
                                   "max_drawdown":"MDD%","expense_ratio_pct":"Expense%","score_100":"Score"})
                  .set_index("rank"), use_container_width=True)

# ════════════════════════════════════════════════════════════
# PAGE 3 — INVESTOR ANALYTICS
# ════════════════════════════════════════════════════════════
elif page == "👥 Investor Analytics":
    st.markdown("<div class='page-header'><h2 style='color:white;margin:0'>👥 Investor Analytics</h2><p style='color:#cce;margin:0'>Demographics, geography and transaction patterns</p></div>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### Filters")
        states   = ["All"] + sorted(tx["state"].dropna().unique().tolist())
        ages     = ["All"] + sorted(tx["age_group"].dropna().unique().tolist())
        genders  = ["All"] + tx["gender"].dropna().unique().tolist()
        tiers    = ["All"] + sorted(tx["city_tier"].dropna().unique().tolist())
        sel_st   = st.selectbox("State",      states)
        sel_age  = st.selectbox("Age Group",  ages)
        sel_gen  = st.selectbox("Gender",     genders)
        sel_tier = st.selectbox("City Tier",  tiers)

    dft = tx.copy()
    if sel_st   != "All": dft = dft[dft["state"]     == sel_st]
    if sel_age  != "All": dft = dft[dft["age_group"] == sel_age]
    if sel_gen  != "All": dft = dft[dft["gender"]    == sel_gen]
    if sel_tier != "All": dft = dft[dft["city_tier"] == sel_tier]

    c1,c2,c3,c4 = st.columns(4)
    kpi(c1, f"₹{dft['amount_inr'].sum()/1e7:,.1f} Cr", "Total Invested")
    kpi(c2, f"{len(dft):,}", "Total Transactions")
    kpi(c3, f"₹{dft['amount_inr'].mean():,.0f}", "Avg Ticket Size")
    kpi(c4, f"{dft['state'].nunique()}", "States Active")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([3,2])
    with col1:
        st.subheader("🗺️ State-wise Transaction Amount")
        state_amt = dft.groupby("state")["amount_inr"].sum().sort_values(ascending=True)/1e7
        fig = px.bar(state_amt.reset_index(), x="amount_inr", y="state", orientation="h",
                     labels={"amount_inr":"Amount (Crore)","state":"State"})
        fig.update_traces(marker_color=SECONDARY)
        st.plotly_chart(blueplot(fig, 450), use_container_width=True)

    with col2:
        st.subheader("🍩 Transaction Type Split")
        tt = dft["transaction_type"].value_counts().reset_index()
        fig = px.pie(tt, names="transaction_type", values="count", hole=0.5,
                     color_discrete_sequence=[SECONDARY, ACCENT, "#E74C3C"])
        st.plotly_chart(blueplot(fig, 280), use_container_width=True)

        st.subheader("⚤ Gender Split")
        gen = dft["gender"].value_counts().reset_index()
        fig = px.pie(gen, names="gender", values="count", hole=0.5,
                     color_discrete_sequence=["#AED6F1","#F9A7B0"])
        st.plotly_chart(blueplot(fig, 260), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("👤 Age Group — Avg SIP Amount")
        age_order = ["18-25","26-35","36-45","46-55","56+"]
        age_avg = dft.groupby("age_group")["amount_inr"].mean().reindex(
            [a for a in age_order if a in dft["age_group"].unique()]).reset_index()
        fig = px.bar(age_avg, x="age_group", y="amount_inr",
                     labels={"amount_inr":"Avg Amount (INR)","age_group":"Age Group"},
                     color="amount_inr", color_continuous_scale=[[0,ACCENT],[1,PRIMARY]])
        st.plotly_chart(blueplot(fig, 340), use_container_width=True)

    with col4:
        st.subheader("📅 Monthly Transaction Volume")
        dft2 = dft.copy()
        dft2["month"] = dft2["transaction_date"].dt.to_period("M").dt.to_timestamp()
        mv = dft2.groupby(["month","transaction_type"])["amount_inr"].sum().reset_index()
        mv["amount_cr"] = mv["amount_inr"]/1e7
        fig = px.line(mv, x="month", y="amount_cr", color="transaction_type",
                      labels={"amount_cr":"Amount (Crore)","month":"Month"})
        st.plotly_chart(blueplot(fig, 340), use_container_width=True)

    st.subheader("🏙️ T30 vs B30 City Tier Distribution")
    tier_amt = dft.groupby("city_tier")["amount_inr"].sum().reset_index()
    fig = px.pie(tier_amt, names="city_tier", values="amount_inr", hole=0.45,
                 color_discrete_sequence=[PRIMARY, ACCENT])
    st.plotly_chart(blueplot(fig, 320), use_container_width=True)

# ════════════════════════════════════════════════════════════
# PAGE 4 — SIP & MARKET TRENDS
# ════════════════════════════════════════════════════════════
elif page == "💰 SIP & Market Trends":
    st.markdown("<div class='page-header'><h2 style='color:white;margin:0'>💰 SIP & Market Trends</h2><p style='color:#cce;margin:0'>SIP flows, category rotation and market correlation</p></div>", unsafe_allow_html=True)

    nifty50 = bench[bench["index_name"]=="NIFTY50"].set_index("date")["close_value"].resample("MS").last().reset_index()

    c1,c2,c3,c4 = st.columns(4)
    kpi(c1, f"₹{sip_m['sip_inflow_crore'].sum():,.0f} Cr", "Total SIP Inflows")
    kpi(c2, f"₹{sip_m['sip_inflow_crore'].max():,.0f} Cr", "Peak Monthly SIP")
    kpi(c3, f"₹{sip_m['sip_inflow_crore'].mean():,.0f} Cr", "Avg Monthly SIP")
    kpi(c4, f"{sip_m['sip_inflow_crore'].pct_change().mean()*100:.1f}%", "Avg Monthly Growth")
    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("📊 Monthly SIP Inflows vs NIFTY50 (Dual-Axis)")
    merged_sip = pd.merge(sip_m, nifty50, left_on="month", right_on="date", how="inner")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=merged_sip["month"], y=merged_sip["sip_inflow_crore"],
                         name="SIP Inflows (Crore)", marker_color=SECONDARY, opacity=0.8), secondary_y=False)
    fig.add_trace(go.Scatter(x=merged_sip["date"], y=merged_sip["close_value"],
                             name="NIFTY50", line=dict(color="#E74C3C", width=2.5)), secondary_y=True)
    fig.update_yaxes(title_text="SIP Inflows (Crore)", secondary_y=False)
    fig.update_yaxes(title_text="NIFTY50 Level", secondary_y=True)
    fig.update_layout(plot_bgcolor=WHITE, paper_bgcolor=WHITE,
                      font=dict(color=PRIMARY), height=420, margin=dict(l=20,r=20,t=30,b=20))
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🌡️ Category Inflow Heatmap")
        cat_i["month_str"] = cat_i["month"].dt.strftime("%Y-%m")
        pivot = cat_i.pivot_table(values="net_inflow_crore", index="category",
                                  columns="month_str", aggfunc="sum")
        fig = px.imshow(pivot, color_continuous_scale=[[0,"#E74C3C"],[0.5,WHITE],[1,SECONDARY]],
                        aspect="auto", labels=dict(color="Net Inflow (Cr)"))
        st.plotly_chart(blueplot(fig, 400), use_container_width=True)

    with col2:
        st.subheader("📈 Folio Count Growth")
        fig = px.area(folio, x="month", y="total_folios_crore",
                      labels={"total_folios_crore":"Folios (Crore)","month":"Month"})
        fig.update_traces(line_color=PRIMARY, fillcolor=f"rgba(0,51,102,0.15)")
        st.plotly_chart(blueplot(fig, 280), use_container_width=True)

        st.subheader("🏆 Top Categories by Latest Inflow")
        latest_cat = cat_i[cat_i["month"]==cat_i["month"].max()].sort_values("net_inflow_crore",ascending=False).head(6)
        fig = px.bar(latest_cat, x="net_inflow_crore", y="category", orientation="h",
                     color="net_inflow_crore", color_continuous_scale=[[0,ACCENT],[1,PRIMARY]])
        st.plotly_chart(blueplot(fig, 280), use_container_width=True)

    # ── What-If SIP Calculator ────────────────────────────────
    st.markdown("---")
    st.subheader("🧮 SIP Wealth Calculator (What-If Analysis)")
    wc1, wc2, wc3 = st.columns(3)
    sip_amt  = wc1.slider("Monthly SIP (₹)", 1000, 50000, 5000, step=500)
    sip_yrs  = wc2.slider("Investment Period (Years)", 1, 30, 10)
    exp_ret  = wc3.slider("Expected Annual Return (%)", 6, 25, 12)

    months  = sip_yrs * 12
    r       = exp_ret / 100 / 12
    fv      = sip_amt * ((((1+r)**months) - 1) / r) * (1+r)
    invested = sip_amt * months
    gain    = fv - invested

    rc1, rc2, rc3 = st.columns(3)
    kpi(rc1, f"₹{invested/1e5:.2f}L", "Total Invested")
    kpi(rc2, f"₹{gain/1e5:.2f}L",     "Wealth Gain")
    kpi(rc3, f"₹{fv/1e5:.2f}L",       "Final Corpus")

    # Growth curve
    xs = list(range(1, months+1))
    ys = [sip_amt * ((((1+r)**m) - 1) / r) * (1+r) for m in xs]
    inv_curve = [sip_amt * m for m in xs]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, name="Projected Corpus",
                             fill="tozeroy", line=dict(color=PRIMARY, width=2.5)))
    fig.add_trace(go.Scatter(x=xs, y=inv_curve, name="Amount Invested",
                             line=dict(color=SECONDARY, dash="dash", width=2)))
    fig.update_layout(xaxis_title="Months", yaxis_title="Amount (₹)",
                      plot_bgcolor=WHITE, paper_bgcolor=WHITE,
                      font=dict(color=PRIMARY), height=350, margin=dict(l=20,r=20,t=20,b=20))
    st.plotly_chart(fig, use_container_width=True)

st.markdown(f"""<hr><center style='color:{PRIMARY};font-size:.8rem'>
Bluestock Fintech Capstone — Mutual Fund Analytics Dashboard © 2025
</center>""", unsafe_allow_html=True)
