"""Supply-chain disruption workspace with an executable inventory mitigation agent."""

import datetime
import json
import os

import plotly.graph_objects as go
import streamlit as st

from agent import SupplyChainAgent
from tools import (
    ERP_DATABASE,
    check_inventory_impact,
    execute_stock_rebalance_order,
    format_inr,
    find_replenishment_options,
    get_product_info,
)


st.set_page_config(
    page_title="Supply Chain Operations",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --ink:#202631; --muted:#7d8796; --line:#e8ebf0; --paper:#ffffff; --canvas:#f5f6f8; --violet:#7356d8; --mint:#18a77b; }
.stApp { background:#f5f6f8; color:var(--ink); font-family:'DM Sans',sans-serif; }
[data-testid="stHeader"] { background:rgba(245,246,248,.94); }
[data-testid="stSidebar"] { background:#fff; border-right:1px solid #e9ebef; }
[data-testid="stSidebar"] > div:first-child { padding-top:1rem; }
.block-container { max-width:1500px; padding-top:1.15rem; padding-bottom:3rem; }
h1,h2,h3 { font-family:'Manrope','DM Sans',sans-serif; color:#202631; }
.brand { font:800 1.08rem 'Manrope',sans-serif; letter-spacing:-.04em; color:#272d39; padding:.25rem .35rem 1.2rem; }
.brand span { color:#7859df; }
.side-label { color:#98a0ad; font-size:.68rem; letter-spacing:.11em; font-weight:700; margin:1.25rem .4rem .45rem; }
.side-link { padding:.57rem .7rem; margin:.15rem 0; border-radius:9px; color:#677182; font-size:.88rem; }
.side-link-active { background:#f1edff; color:#6345cf; font-weight:700; }
.side-card { margin-top:1.5rem; padding:.9rem; border:1px solid #eeeef2; border-radius:12px; color:#657080; font-size:.78rem; line-height:1.5; background:#fbfbfd; }
.page-top { display:flex; align-items:center; justify-content:space-between; margin-bottom:.15rem; }
.eyebrow { text-transform:uppercase; font-size:.67rem; letter-spacing:.12em; font-weight:700; color:#7e8795; }
.title { font:800 1.5rem 'Manrope',sans-serif; letter-spacing:-.05em; color:#222936; margin:.15rem 0; }
.subtitle { color:#858d9b; font-size:.81rem; }
.live-pill { border:1px solid #dcefe8; background:#f1faf6; color:#19825f; padding:.43rem .7rem; border-radius:999px; font-size:.73rem; font-weight:700; }
.top-actions { display:flex; gap:.4rem; }
.kpi { background:#fff; border:1px solid #e9ebef; border-radius:13px; padding:1rem 1.05rem; min-height:112px; box-shadow:0 2px 9px rgba(23,34,55,.025); }
.kpi-label { color:#7d8795; font-size:.74rem; font-weight:600; }
.kpi-value { color:#222936; font:800 1.48rem 'Manrope',sans-serif; letter-spacing:-.04em; margin:.36rem 0 .2rem; }
.kpi-foot { color:#8b93a0; font-size:.69rem; }
.positive { color:#138861; font-weight:700; }
.negative { color:#d16d51; font-weight:700; }
.panel { background:#fff; border:1px solid #e9ebef; border-radius:13px; padding:1rem 1.05rem; box-shadow:0 2px 9px rgba(23,34,55,.025); }
.panel-title { color:#252b37; font:700 .92rem 'Manrope',sans-serif; }
.panel-sub { color:#8c94a1; font-size:.7rem; margin-top:.17rem; }
.section-head { display:flex; justify-content:space-between; align-items:center; padding-bottom:.65rem; }
.small-tag { color:#777f8e; font-size:.68rem; padding:.3rem .5rem; background:#f5f6f8; border-radius:6px; }
.strategy { border:1px solid #eceef2; border-radius:9px; padding:.6rem .7rem; margin:.45rem 0; }
.strategy-head { display:flex; justify-content:space-between; color:#333b49; font-size:.75rem; font-weight:700; }
.strategy-sub { color:#939aa6; font-size:.67rem; margin-top:.2rem; }
.save-box { background:#f0faf6; border:1px solid #d9f0e6; padding:.75rem; border-radius:10px; margin:.55rem 0; }
.save-label { color:#56816f; font-size:.69rem; }
.save-value { color:#16845f; font:800 1.15rem 'Manrope',sans-serif; margin-top:.15rem; }
.notice { color:#727c8c; background:#f8f8fb; border:1px solid #eeeef3; border-radius:9px; padding:.65rem .75rem; font-size:.7rem; line-height:1.45; }
[data-testid="stMetric"] { background:transparent; }
div[data-testid="stSelectbox"] label, div[data-testid="stSlider"] label, div[data-testid="stTextInput"] label { font-size:.72rem; color:#6f7887; }
div[data-testid="stButton"] button[kind="primary"] { border:0; background:#7052d3; color:#fff; border-radius:9px; min-height:2.55rem; font-weight:700; }
div[data-testid="stButton"] button[kind="primary"]:hover { background:#5f43bd; border:0; }
div[data-testid="stTabs"] button { color:#7a8391; font-size:.77rem; }
div[data-testid="stTabs"] button[aria-selected="true"] { color:#694bcf; }
div[data-testid="stDataFrame"] { border:1px solid #eef0f3; border-radius:8px; overflow:hidden; }
.footnote { color:#9aa1ac; font-size:.66rem; }
.sc-flow { margin:1rem 0 1.2rem; padding:1.15rem 1.25rem 1rem; background:linear-gradient(115deg,#fff 0%,#fbfaff 56%,#f5fbf8 100%); border:1px solid #e8ebf0; border-radius:15px; box-shadow:0 3px 14px rgba(23,34,55,.035); overflow:hidden; }
.sc-flow-head { display:flex; justify-content:space-between; align-items:center; gap:1rem; }
.sc-flow-title { color:#252b37; font:700 .95rem 'Manrope',sans-serif; }
.sc-flow-tag { color:#19825f; background:#eef9f4; border:1px solid #d9efe5; border-radius:999px; padding:.28rem .55rem; font:700 .62rem 'DM Sans',sans-serif; letter-spacing:.08em; white-space:nowrap; }
.sc-track { height:38px; position:relative; margin:.55rem .55rem .05rem; }
.sc-track-line { position:absolute; left:4%; right:4%; top:18px; height:3px; border-radius:4px; background:linear-gradient(90deg,#e0d9fb,#c9e9db); overflow:hidden; }
.sc-track-line:after { content:''; display:block; height:100%; width:38%; background:linear-gradient(90deg,transparent,#7356d8,#18a77b,transparent); animation:sc-line-flow 3.4s linear infinite; }
.sc-parcel { position:absolute; z-index:2; top:1px; left:2%; width:34px; height:34px; display:grid; place-items:center; border-radius:10px; background:#fff; border:1px solid #e7e4f5; box-shadow:0 3px 8px rgba(67,53,132,.12); font-size:17px; animation:sc-parcel-travel 8s cubic-bezier(.45,0,.55,1) infinite; }
.sc-flow-steps { display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:.5rem; }
.sc-flow-step { position:relative; z-index:1; text-align:center; padding:.05rem .2rem .2rem; animation:sc-step-glow 8s ease-in-out infinite; }
.sc-flow-step:nth-child(2) { animation-delay:1.3s; }
.sc-flow-step:nth-child(3) { animation-delay:2.6s; }
.sc-flow-step:nth-child(4) { animation-delay:3.9s; }
.sc-flow-step:nth-child(5) { animation-delay:5.2s; }
.sc-flow-icon { width:37px; height:37px; margin:0 auto .35rem; display:grid; place-items:center; border-radius:12px; background:#fff; border:1px solid #e8ebf0; box-shadow:0 2px 7px rgba(23,34,55,.035); font-size:17px; }
.sc-flow-step strong { display:block; color:#333b49; font:700 .7rem 'DM Sans',sans-serif; }
.sc-flow-step span { display:block; margin-top:.18rem; color:#858d9b; font:400 .62rem 'DM Sans',sans-serif; line-height:1.35; }
@keyframes sc-line-flow { from { transform:translateX(-120%); } to { transform:translateX(300%); } }
@keyframes sc-parcel-travel { 0%,5% { left:2%; } 45%,55% { left:calc(50% - 17px); } 95%,100% { left:calc(98% - 34px); } }
@keyframes sc-step-glow { 0%,12%,100% { transform:translateY(0); } 5% { transform:translateY(-3px); } }
@media (max-width:800px) { .sc-flow-steps { grid-template-columns:repeat(2,minmax(0,1fr)); row-gap:.7rem; } .sc-flow-step:last-child { grid-column:1 / -1; } .sc-track { margin-left:.2rem; margin-right:.2rem; } }
@media (prefers-reduced-motion:reduce) { .sc-track-line:after,.sc-parcel,.sc-flow-step { animation:none !important; } .sc-parcel { left:calc(50% - 17px); } }
.page-motion { margin:.4rem 0 1rem; padding:.9rem 1rem; border:1px solid #e8ebf0; border-radius:13px; background:linear-gradient(110deg,#fff,#f8f7ff 65%,#f2faf6); overflow:hidden; animation:pm-enter .45s ease-out both; }
.pm-heading { display:flex; justify-content:space-between; align-items:center; gap:.75rem; color:#343b49; font:700 .78rem 'Manrope',sans-serif; }
.pm-heading small { color:#8c94a1; font:500 .63rem 'DM Sans',sans-serif; }
.pm-visual { min-height:112px; margin-top:.55rem; border:1px solid #ececf2; border-radius:11px; background:rgba(255,255,255,.78); overflow:hidden; position:relative; }
.pm-caption { color:#8c94a1; font:400 .62rem 'DM Sans',sans-serif; margin-top:.5rem; }
.pm-network { display:grid; grid-template-columns:1.15fr 2fr; align-items:center; gap:1rem; padding:.65rem 1rem; min-height:112px; }
.pm-network-map { width:100%; height:95px; }
.pm-net-route { fill:none; stroke:#cfc8f3; stroke-width:2; stroke-dasharray:5 6; animation:pm-dash 3s linear infinite; }
.pm-node { fill:#fff; stroke:#7356d8; stroke-width:2; transform-box:fill-box; transform-origin:center; animation:pm-node 2.4s ease-in-out infinite; }
.pm-node:nth-of-type(2) { animation-delay:.4s; } .pm-node:nth-of-type(3) { animation-delay:.8s; } .pm-node:nth-of-type(4) { animation-delay:1.2s; }
.pm-hub-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:.35rem; }
.pm-hub { text-align:center; color:#70798a; font:600 .59rem 'DM Sans',sans-serif; }
.pm-hub i { display:block; width:100%; max-width:42px; height:32px; margin:0 auto .25rem; border-radius:7px 7px 3px 3px; background:linear-gradient(180deg,#b8e8d7,#e7f7f0); border:1px solid #d6eee4; transform-origin:bottom; animation:pm-stock 1.8s ease-in-out infinite alternate; }
.pm-hub:nth-child(2) i { animation-delay:.2s; } .pm-hub:nth-child(3) i { animation-delay:.4s; } .pm-hub:nth-child(4) i { animation-delay:.6s; } .pm-hub:nth-child(5) i { animation-delay:.8s; }
.pm-timeline { padding:1rem 1.25rem .7rem; }
.pm-route { height:4px; margin:.65rem 5% 1rem; border-radius:9px; background:linear-gradient(90deg,#d8d0fb,#bde9d7); position:relative; }
.pm-route:after { content:'📦'; position:absolute; top:-17px; left:0; font-size:20px; animation:pm-travel 6s ease-in-out infinite; }
.pm-stops { display:grid; grid-template-columns:repeat(5,1fr); text-align:center; gap:.4rem; }
.pm-stop { color:#677182; font:600 .62rem 'DM Sans',sans-serif; }
.pm-stop b { display:grid; place-items:center; width:23px; height:23px; margin:0 auto .3rem; border-radius:50%; background:#f1edff; color:#674bcc; font-size:.62rem; box-shadow:0 0 0 0 rgba(115,86,216,.25); animation:pm-ring 2.5s ease-out infinite; }
.pm-stop:nth-child(2) b { animation-delay:.4s; } .pm-stop:nth-child(3) b { animation-delay:.8s; } .pm-stop:nth-child(4) b { animation-delay:1.2s; } .pm-stop:nth-child(5) b { animation-delay:1.6s; }
.pm-supplier-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:.65rem; padding:.65rem; }
.pm-supplier { padding:.55rem .65rem; border:1px solid #ececf2; border-radius:9px; color:#637082; font:600 .61rem 'DM Sans',sans-serif; }
.pm-supplier strong { display:block; color:#353d4a; font-size:.67rem; margin-bottom:.15rem; }
.pm-costbar { height:7px; margin-top:.42rem; border-radius:9px; background:#efedf6; overflow:hidden; }
.pm-costbar i { display:block; height:100%; width:var(--bar); border-radius:9px; background:linear-gradient(90deg,#9279e4,#7356d8); transform-origin:left; animation:pm-grow 2s ease-out both infinite alternate; }
.pm-supplier:nth-child(2) .pm-costbar i { background:linear-gradient(90deg,#6bc99f,#18a77b); animation-delay:.3s; }
.pm-supplier:nth-child(3) .pm-costbar i { background:linear-gradient(90deg,#f0bf71,#d99444); animation-delay:.6s; }
.pm-risk { display:grid; grid-template-columns:auto 1fr; align-items:center; gap:1.5rem; padding:.6rem 1.1rem; min-height:112px; }
.pm-gauge { width:82px; height:82px; border-radius:50%; display:grid; place-items:center; background:conic-gradient(#d7775a 0 68%,#f1edf9 68% 100%); animation:pm-rotate 8s linear infinite; position:relative; }
.pm-gauge:after { content:''; position:absolute; inset:8px; border-radius:50%; background:#fff; }
.pm-gauge span { position:relative; z-index:1; color:#c6674d; font:800 .76rem 'Manrope',sans-serif; }
.pm-risk-bars { display:grid; gap:.48rem; }
.pm-riskbar { display:grid; grid-template-columns:100px 1fr; align-items:center; gap:.5rem; color:#70798a; font:600 .6rem 'DM Sans',sans-serif; }
.pm-riskbar i { display:block; height:8px; border-radius:8px; background:linear-gradient(90deg,#eda47f,#d7775a); transform-origin:left; animation:pm-grow 2.2s ease-out infinite alternate; }
.pm-riskbar:nth-child(2) i { width:66% !important; animation-delay:.3s; background:linear-gradient(90deg,#bea9f2,#7356d8); }
.pm-riskbar:nth-child(3) i { width:42% !important; animation-delay:.6s; background:linear-gradient(90deg,#f3cf8d,#d99a42); }
.pm-agent { display:grid; grid-template-columns:repeat(3,1fr); align-items:center; gap:1rem; padding:.8rem 1.2rem; }
.pm-tool { text-align:center; color:#687284; font:600 .64rem 'DM Sans',sans-serif; position:relative; }
.pm-tool:not(:last-child):after { content:'⟶'; position:absolute; top:12px; right:-1rem; color:#9a88de; font-size:1.05rem; animation:pm-arrow 1.8s ease-in-out infinite; }
.pm-tool:nth-child(2):after { animation-delay:.4s; }
.pm-orb { display:grid; place-items:center; width:40px; height:40px; margin:0 auto .32rem; border-radius:13px; color:#6b50cc; background:#f0ecff; border:1px solid #e0d9fb; box-shadow:0 0 0 0 rgba(115,86,216,.3); animation:pm-orb 2.4s ease-out infinite; font:800 .72rem 'Manrope',sans-serif; }
.pm-tool:nth-child(2) .pm-orb { animation-delay:.5s; } .pm-tool:nth-child(3) .pm-orb { animation-delay:1s; }
.pm-config { display:grid; grid-template-columns:repeat(4,1fr); gap:.7rem; padding:.8rem; }
.pm-field { border:1px solid #ececf2; border-radius:9px; padding:.55rem .65rem; color:#7b8492; font:600 .58rem 'DM Sans',sans-serif; background:#fff; }
.pm-field b { display:block; color:#424a58; font-size:.65rem; margin-top:.28rem; }
.pm-slider { height:5px; background:#efedf6; border-radius:8px; margin-top:.48rem; position:relative; overflow:hidden; }
.pm-slider i { display:block; height:100%; width:62%; border-radius:8px; background:#8c73de; animation:pm-slide 2.4s ease-in-out infinite alternate; }
@keyframes pm-enter { from { opacity:.25; transform:translateY(5px); } to { opacity:1; transform:translateY(0); } }
@keyframes pm-dash { to { stroke-dashoffset:-44; } } @keyframes pm-node { 50% { transform:scale(1.35); fill:#e7e1ff; } }
@keyframes pm-stock { to { transform:scaleY(.65); filter:saturate(.65); } } @keyframes pm-travel { 0%,7% { left:0; } 48%,55% { left:calc(50% - 10px); } 93%,100% { left:calc(100% - 20px); } }
@keyframes pm-ring { 70% { box-shadow:0 0 0 9px rgba(115,86,216,0); } 100% { box-shadow:0 0 0 0 rgba(115,86,216,0); } }
@keyframes pm-grow { from { transform:scaleX(.74); opacity:.72; } to { transform:scaleX(1); opacity:1; } }
@keyframes pm-rotate { to { transform:rotate(360deg); } } @keyframes pm-arrow { 50% { transform:translateX(4px); opacity:.55; } }
@keyframes pm-orb { 70% { box-shadow:0 0 0 10px rgba(115,86,216,0); } 100% { box-shadow:0 0 0 0 rgba(115,86,216,0); } }
@keyframes pm-slide { to { width:83%; } }
@media (max-width:700px) { .pm-network { grid-template-columns:1fr; } .pm-network-map { height:70px; } .pm-config { grid-template-columns:repeat(2,1fr); } .pm-risk { gap:.7rem; } }
@media (prefers-reduced-motion:reduce) { .page-motion *,.sc-flow * { animation:none !important; } }
[data-testid="stSidebar"] div[data-testid="stButton"] button { width:100%; text-align:left; border:0; background:transparent; color:#677182; border-radius:9px; padding:.55rem .7rem; }
[data-testid="stSidebar"] div[data-testid="stButton"] button:hover { background:#f7f5ff; color:#6345cf; }
[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] { background:#f1edff; color:#6345cf; font-weight:700; }
</style>
""", unsafe_allow_html=True)


PAGES = {
    "Disruption Overview": "◈  Disruption Overview",
    "Inventory Network": "⌁  Inventory Network",
    "Transfer Orders": "▤  Transfer Orders",
    "Replenishment Sources": "♧  Replenishment Sources",
    "Stockout Exposure": "↗  Stockout Exposure",
    "Agent Activity": "◷  Agent Activity",
    "Scenario Settings": "⚙  Scenario Settings",
}
PRODUCT_LABELS = [f"{sku} · {product['name']}" for sku, product in ERP_DATABASE["products"].items()]
WORKSPACE_PAGES = ["Disruption Overview", "Inventory Network", "Transfer Orders", "Replenishment Sources"]
OPERATIONS_PAGES = ["Stockout Exposure", "Agent Activity", "Scenario Settings"]

for key, value in {
    "current_page": "Disruption Overview",
    "scenario_name": "Port congestion",
    "scenario_sku": "SKU-402",
    "scenario_destination": "WH-MUM",
    "scenario_delay": 12,
    "scenario_prompt": "Supplier shipment delayed by congestion at Nhava Sheva port",
    "scenario_incident_id": "INC-PORT-MUM-402-001",
    "monitor_enabled": False,
    "monitor_interval_seconds": 30,
    "agent_activity": [],
    "monitor_history": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

with st.sidebar:
    st.markdown('<div class="brand">NEXUS<span> /</span> OPS</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-label">WORKSPACE</div>', unsafe_allow_html=True)
    for nav_page in WORKSPACE_PAGES:
        if st.button(PAGES[nav_page], key=f"nav_{nav_page}", type="primary" if st.session_state["current_page"] == nav_page else "secondary"):
            st.session_state["current_page"] = nav_page
            st.rerun()
    st.markdown('<div class="side-label">OPERATIONS</div>', unsafe_allow_html=True)
    for nav_page in OPERATIONS_PAGES:
        if st.button(PAGES[nav_page], key=f"nav_{nav_page}", type="primary" if st.session_state["current_page"] == nav_page else "secondary"):
            st.session_state["current_page"] = nav_page
            st.rerun()
    st.markdown("""
    <div class="side-card"><b style="color:#313846">Nexus Ops Agent</b><br/>
    Autonomous sourcing and inventory rebalance<br/><br/>
    <span style="color:#15926b">●</span> Simulation systems ready</div>
    """, unsafe_allow_html=True)
    st.caption("Workspace · Operations Team")

page = st.session_state["current_page"]
page_titles = {
    "Disruption Overview": ("India supply chain operations / Disruption desk", "India Supply Disruption & Inventory Rebalancing", "Assess risk, compare replenishment routes, and run the autonomous mitigation agent."),
    "Inventory Network": ("Workspace / Inventory", "Inventory Network", "Inspect simulated stock, reservations, and demand across hubs."),
    "Transfer Orders": ("Workspace / Execution ledger", "Transfer Orders", "Review transfer orders created by the autonomous agent in this session."),
    "Replenishment Sources": ("Workspace / Sourcing", "Replenishment Sources", "Compare internal transfers and spot supply for a selected inventory gap."),
    "Stockout Exposure": ("Operations / Risk assessment", "Stockout Exposure", "Calculate units at risk, days of cover, and estimated financial exposure."),
    "Agent Activity": ("Operations / Audit trail", "Agent Activity", "Review the reasoning and tool observations from recent agent runs."),
    "Scenario Settings": ("Operations / Configuration", "Scenario Settings", "Configure the disruption, product, destination, and delay used by the overview."),
}
eyebrow, title, subtitle = page_titles[page]
header_left, header_right = st.columns([4, 1])
with header_left:
    st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">{subtitle}</div>', unsafe_allow_html=True)
with header_right:
    st.markdown('<div style="text-align:right;padding-top:.4rem"><span class="live-pill">● SIMULATION DATA</span></div>', unsafe_allow_html=True)

def _warehouse_label(warehouse_id):
    return f"{warehouse_id} · {ERP_DATABASE['warehouses'][warehouse_id]['name'].split('(')[-1].rstrip(')')}"

def _run_assessment(sku, destination, delay):
    impact = json.loads(check_inventory_impact(sku, int(delay), destination))
    if "error" in impact:
        st.error(impact["error"])
        return None, None
    options = None
    if impact["projected_stockout_units"] > 0:
        options = json.loads(find_replenishment_options(sku, impact["projected_stockout_units"], destination))
    return impact, options

@st.fragment(run_every=st.session_state["monitor_interval_seconds"] if st.session_state["monitor_enabled"] else None)
def _periodic_inventory_monitor():
    if not st.session_state["monitor_enabled"]:
        return
    incident_id = st.session_state["scenario_incident_id"].strip()
    sku = st.session_state["scenario_sku"]
    destination = st.session_state["scenario_destination"]
    delay = int(st.session_state["scenario_delay"])
    scenario_name = st.session_state["scenario_name"]
    if not incident_id:
        st.error("Monitoring is enabled, but this incident has no incident ID. Add one in Scenario Settings.")
        return

    with st.container(border=True):
        st.markdown("**Periodic disruption monitor · active**")
        try:
            impact = json.loads(check_inventory_impact(sku, delay, destination))
            if "error" in impact:
                raise ValueError(impact["error"])
            existing_order = next((order for order in reversed(ERP_DATABASE["transfer_orders"])
                                   if order.get("incident_id") == incident_id
                                   and order.get("status") == "AUTHORIZED_AND_DISPATCHED"), None)
            action = "No stockout risk detected."
            order_id = None
            if existing_order:
                action = f"Incident already has dispatched order {existing_order['order_id']}; no duplicate order created."
                order_id = existing_order["order_id"]
            elif impact["projected_stockout_units"] > 0:
                sourcing = json.loads(find_replenishment_options(sku, impact["projected_stockout_units"], destination))
                if "error" in sourcing:
                    raise ValueError(sourcing["error"])
                safe_options = [option for option in sourcing.get("options", [])
                                if option.get("covers_full_deficit")
                                and option.get("transit_time_days", 999) <= impact["days_of_supply_remaining"]]
                if safe_options:
                    choice = safe_options[0]
                    order_result = json.loads(execute_stock_rebalance_order(
                        sku=sku,
                        source_wh_or_vendor=choice["source_id"],
                        destination_wh=destination,
                        quantity=choice["offered_quantity"],
                        expedited=True,
                        incident_id=incident_id,
                    ))
                    if order_result.get("success"):
                        order_id = order_result["order_details"]["order_id"]
                        if order_result.get("duplicate_prevented"):
                            action = f"Incident already has dispatched order {order_id}; no duplicate order created."
                        else:
                            action = f"Auto-dispatched {choice['offered_quantity']} units from {choice['source_name']} · order {order_id}."
                    else:
                        action = "Order was not placed: " + order_result.get("error", "unknown tool error")
                else:
                    action = "Stockout exposure detected, but no full-coverage option arrives before stockout. Manual escalation needed."
            record = {"checked_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                      "incident_id": incident_id, "sku": sku, "destination": destination,
                      "status": impact["status"], "deficit_units": impact["projected_stockout_units"],
                      "exposure_inr": impact["financial_risk"]["total_risk_exposure_inr"],
                      "action": action, "order_id": order_id}
            if not st.session_state["monitor_history"] or st.session_state["monitor_history"][-1] != record:
                st.session_state["monitor_history"].append(record)
                st.session_state["monitor_history"] = st.session_state["monitor_history"][-50:]
            if order_id and action.startswith("Auto-dispatched"):
                st.success(action)
            elif impact["projected_stockout_units"] > 0 and not existing_order:
                st.warning(action)
            else:
                st.info(action)
            st.caption(f"Incident {incident_id} · {sku} · {destination} · next scan in {st.session_state['monitor_interval_seconds']} sec")
        except Exception as error:
            st.error(f"Monitor cycle failed safely: {error}")

_periodic_inventory_monitor()

PAGE_MOTION = {
    "Inventory Network": {
        "title": "Regional inventory network",
        "note": "A schematic network scan: available stock is calculated after reservations and safety buffers.",
        "visual": '''<div class="pm-visual pm-network"><svg class="pm-network-map" viewBox="0 0 240 100" role="img" aria-label="Five connected Indian warehouse hubs"><path class="pm-net-route" d="M30 52 L80 20 L130 52 L180 20 L215 56 M30 52 L80 82 L130 52 L180 82 L215 56 M80 20 L180 82 M80 82 L180 20"/><circle class="pm-node" cx="30" cy="52" r="8"/><circle class="pm-node" cx="80" cy="20" r="8"/><circle class="pm-node" cx="130" cy="52" r="9"/><circle class="pm-node" cx="180" cy="20" r="8"/><circle class="pm-node" cx="215" cy="56" r="8"/></svg><div class="pm-hub-grid"><div class="pm-hub"><i></i>MUM</div><div class="pm-hub"><i></i>DEL</div><div class="pm-hub"><i></i>BLR</div><div class="pm-hub"><i></i>CHE</div><div class="pm-hub"><i></i>KOL</div></div></div>''',
    },
    "Transfer Orders": {
        "title": "Transfer order lifecycle",
        "note": "Illustrative order timeline; the moving parcel does not indicate an order has been dispatched.",
        "visual": '''<div class="pm-visual pm-timeline"><div class="pm-route"></div><div class="pm-stops"><div class="pm-stop"><b>1</b>Order created</div><div class="pm-stop"><b>2</b>Stock reserved</div><div class="pm-stop"><b>3</b>Carrier booked</div><div class="pm-stop"><b>4</b>In transit</div><div class="pm-stop"><b>5</b>Hub receives</div></div></div>''',
    },
    "Replenishment Sources": {
        "title": "Replenishment source comparison",
        "note": "Illustrative quote bars show the evaluation sequence. Use the form below for current simulated quotes.",
        "visual": '''<div class="pm-visual pm-supplier-grid"><div class="pm-supplier"><strong>Regional hub</strong>Safety-stock check<div class="pm-costbar"><i style="--bar:42%"></i></div></div><div class="pm-supplier"><strong>Approved supplier</strong>Capacity + lead time<div class="pm-costbar"><i style="--bar:72%"></i></div></div><div class="pm-supplier"><strong>Rush supplier</strong>Premium + freight<div class="pm-costbar"><i style="--bar:90%"></i></div></div></div>''',
    },
    "Stockout Exposure": {
        "title": "Stockout exposure analysis",
        "note": "Bars are a conceptual animation; the form below calculates the selected item's exposure.",
        "visual": '''<div class="pm-visual pm-risk"><div class="pm-gauge"><span>RISK</span></div><div class="pm-risk-bars"><div class="pm-riskbar"><span>Stock cover</span><i style="width:31%"></i></div><div class="pm-riskbar"><span>Revenue exposure</span><i style="width:66%"></i></div><div class="pm-riskbar"><span>SLA penalties</span><i style="width:42%"></i></div></div></div>''',
    },
    "Agent Activity": {
        "title": "Agent decision trace",
        "note": "The three tool stages are audited below, followed by the periodic monitor's scan log.",
        "visual": '''<div class="pm-visual pm-agent"><div class="pm-tool"><div class="pm-orb">01</div>Assess impact</div><div class="pm-tool"><div class="pm-orb">02</div>Find options</div><div class="pm-tool"><div class="pm-orb">03</div>Commit safely</div></div>''',
    },
    "Scenario Settings": {
        "title": "Scenario configuration flow",
        "note": "Animated controls are illustrative; the settings form below changes the active incident.",
        "visual": '''<div class="pm-visual pm-config"><div class="pm-field">INCIDENT<b>Port congestion</b><div class="pm-slider"><i></i></div></div><div class="pm-field">PRODUCT<b>Servo drive</b><div class="pm-slider"><i></i></div></div><div class="pm-field">DESTINATION<b>Mumbai hub</b><div class="pm-slider"><i></i></div></div><div class="pm-field">DELAY<b>12 days</b><div class="pm-slider"><i></i></div></div></div>''',
    },
}

if page in PAGE_MOTION:
    motion = PAGE_MOTION[page]
    st.markdown(
        f'<div class="page-motion"><div class="pm-heading"><span>{motion["title"]}</span><small>PROCESS ANIMATION</small></div>{motion["visual"]}<div class="pm-caption">{motion["note"]}</div></div>',
        unsafe_allow_html=True,
    )

if page == "Disruption Overview":
    sku = st.session_state["scenario_sku"]
    destination = st.session_state["scenario_destination"]
    delay_days = st.session_state["scenario_delay"]
    impact_preview = json.loads(check_inventory_impact(sku, int(delay_days), destination))
    target_stock = ERP_DATABASE["warehouses"][destination]["stock"][sku]
    product_info = get_product_info(sku)
    available = target_stock["on_hand"] - target_stock["reserved"]
    days_supply = available / target_stock["daily_burn_rate"]
    k1, k2, k3 = st.columns(3)
    k1.metric("Available stock · " + destination, f"{available} units", f"{days_supply:.1f} days of supply")
    k2.metric("Projected deficit", f"{impact_preview.get('projected_stockout_units', 0)} units", f"{delay_days}-day disruption")
    k3.metric("Estimated exposure", format_inr(impact_preview.get('financial_risk', {}).get('total_risk_exposure_inr', 0), 0), product_info["name"])

    destination_name = ERP_DATABASE["warehouses"][destination]["name"].split("(")[0].strip()
    deficit_units = impact_preview.get("projected_stockout_units", 0)
    st.markdown(f"""
    <div class="sc-flow" role="img" aria-label="Animated supply chain flow from disruption alert through inventory assessment and source selection to a simulated transfer into {destination_name}">
      <div class="sc-flow-head"><div class="sc-flow-title">Disruption response · {sku}</div><div class="sc-flow-tag">WORKFLOW ANIMATION</div></div>
      <div class="sc-track"><div class="sc-track-line"></div><div class="sc-parcel" aria-hidden="true">📦</div></div>
      <div class="sc-flow-steps">
        <div class="sc-flow-step"><div class="sc-flow-icon">⚠</div><strong>Disruption alert</strong><span>{st.session_state['scenario_name']} · +{delay_days} days</span></div>
        <div class="sc-flow-step"><div class="sc-flow-icon">◷</div><strong>Assess inventory</strong><span>{days_supply:.1f} days cover · {deficit_units} units at risk</span></div>
        <div class="sc-flow-step"><div class="sc-flow-icon">▦</div><strong>Find safe source</strong><span>Check surplus and safety stock across hubs</span></div>
        <div class="sc-flow-step"><div class="sc-flow-icon">🚚</div><strong>Rebalance stock</strong><span>Choose a full-coverage route that arrives on time</span></div>
        <div class="sc-flow-step"><div class="sc-flow-icon">⌂</div><strong>Destination hub</strong><span>{destination_name} · inbound ETA after dispatch</span></div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Illustrative workflow animation. A transfer order is created only when the agent runs or periodic monitoring dispatches one.")

    main_col, rail_col = st.columns([3.15, 1.05], gap="medium")
    with main_col:
        with st.container(border=True):
            st.markdown(f'<div class="section-head"><div><div class="panel-title">Days of supply by hub · {sku}</div><div class="panel-sub">Available inventory divided by average daily demand</div></div><span class="small-tag">Current snapshot</span></div>', unsafe_allow_html=True)
            chart = go.Figure()
            hub_names, supply_days = [], []
            for warehouse in ERP_DATABASE["warehouses"].values():
                stock = warehouse["stock"].get(sku)
                if stock:
                    hub_names.append(warehouse["name"].split("(")[0].strip())
                    supply_days.append((stock["on_hand"] - stock["reserved"]) / stock["daily_burn_rate"])
            chart.add_trace(go.Bar(x=hub_names, y=supply_days, marker_color="#7356d8", hovertemplate="%{x}<br>%{y:.1f} days<extra></extra>"))
            chart.add_hline(y=days_supply, line_dash="dot", line_color="#d98b6a", annotation_text="Destination cover", annotation_position="top left")
            chart.update_layout(height=280, margin={"l": 5, "r": 5, "t": 8, "b": 5}, paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(0,0,0,0)", font={"family": "DM Sans", "color": "#8992a0", "size": 10},
                                showlegend=False, xaxis={"showgrid": False, "linecolor": "#edf0f3"},
                                yaxis={"showgrid": True, "gridcolor": "#eff1f4", "title": "Days of supply"})
            st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})
            st.caption("All values are simulated local ERP data.")
        with st.container(border=True):
            st.markdown('<div class="panel-title">Autonomous mitigation</div><div class="panel-sub">The agent assesses risk, finds a safe source, then commits a simulated transfer order.</div>', unsafe_allow_html=True)
            api_toggle = st.toggle("Use OpenAI tool calling", value=False)
            api_key = None
            if api_toggle:
                api_key = st.text_input("OpenAI API key", type="password", value=os.getenv("OPENAI_API_KEY", ""), placeholder="sk-...", key="agent_openai_api_key")
                if not api_key and not os.getenv("OPENAI_API_KEY"):
                    st.caption("No API key found. The agent will use the offline engine.")
            if st.button("Run autonomous disruption triage", type="primary", use_container_width=True):
                scenario_details = ERP_DATABASE["scenarios"][st.session_state["scenario_name"]]["description"]
                prompt = f"{st.session_state['scenario_prompt']}. {scenario_details} {sku} to {destination} delayed by {delay_days} days."
                agent = SupplyChainAgent(api_key=api_key if api_toggle else None)
                events, report = [], None
                try:
                    with st.status("Nexus Ops is assessing the disruption…", expanded=True) as status:
                        for event in agent.run_agentic_workflow(prompt, sku=sku, delay_days=int(delay_days), destination_wh=destination, force_demo_mode=not api_toggle, incident_id=st.session_state["scenario_incident_id"]):
                            events.append(event)
                            if event.get("type") == "thought":
                                status.write(event.get("content", ""))
                            elif event.get("type") == "tool_call":
                                status.write(f"Calling {event['tool_name']}…")
                            elif event.get("type") == "final_report":
                                report = event["content"]
                        if report is None:
                            raise RuntimeError("The agent finished without producing an executive report.")
                        status.update(label="Triage complete", state="complete", expanded=False)
                except Exception as error:
                    events.append({"type": "error", "message": str(error)})
                    st.session_state["agent_activity"].append({"prompt": prompt, "events": events, "report": None})
                    st.session_state["last_agent_report"] = None
                    st.error(f"Triage could not complete: {error}")
                else:
                    st.session_state["agent_activity"].append({"prompt": prompt, "events": events, "report": report})
                    st.session_state["last_agent_report"] = report
                    st.rerun()
        report = st.session_state.get("last_agent_report")
        if report:
            st.subheader("Latest mitigation result")
            if report["status"].startswith("RESOLVED"):
                st.success(f"{report['status']} · {report['executive_headline']}")
            else:
                st.warning(f"{report['status']} · {report['executive_headline']}")
            metrics = report["metrics"]
            result_cols = st.columns(4)
            result_cols[0].metric("Exposure protected", format_inr(metrics['revenue_protected_inr'], 0))
            result_cols[1].metric("Transfer freight", format_inr(metrics['rebalance_logistics_cost_inr'], 0))
            result_cols[2].metric("Exposure less freight", format_inr(metrics['net_financial_savings_inr'], 0))
            result_cols[3].metric("Transfer order", metrics["order_tracking_id"])
            latest_run = st.session_state["agent_activity"][-1] if st.session_state["agent_activity"] else {}
            events_by_type = {}
            for run_event in latest_run.get("events", []):
                if run_event.get("type") == "tool_result":
                    events_by_type[run_event.get("tool_name")] = run_event.get("result", {})
            impact_result = events_by_type.get("check_inventory_impact", {})
            sourcing_result = events_by_type.get("find_replenishment_options", {})
            dispatch_result = events_by_type.get("execute_stock_rebalance_order", {})
            with st.expander("Detailed operational review", expanded=False):
                st.caption(f"Incident {st.session_state['scenario_incident_id']} · {len([e for e in latest_run.get('events', []) if e.get('type') == 'tool_call'])} registered tool calls")
                st.markdown("#### Inventory and service impact")
                if impact_result and "error" not in impact_result:
                    risk = impact_result.get("financial_risk", {})
                    impact_cols = st.columns(4)
                    impact_cols[0].metric("Available / reserved", f"{impact_result.get('current_available_units', 0)} units", f"{impact_result.get('reserved_units', 0)} reserved")
                    impact_cols[1].metric("Demand rate", f"{impact_result.get('daily_burn_rate', 0)} units/day")
                    impact_cols[2].metric("Days of supply", f"{impact_result.get('days_of_supply_remaining', 0):.1f}", f"Reorder point {impact_result.get('reorder_point_units', 0)} units")
                    impact_cols[3].metric("Deficit window", f"{impact_result.get('deficit_days', 0):.1f} days", f"{impact_result.get('projected_stockout_units', 0)} units short")
                    risk_rows = [
                        {"Exposure measure": "Unfulfilled revenue risk", "Amount": format_inr(risk.get('unfulfilled_revenue_risk_inr', 0))},
                        {"Exposure measure": "Gross margin at risk · context", "Amount": format_inr(risk.get('gross_margin_at_risk_inr', 0))},
                        {"Exposure measure": "SLA breach penalties", "Amount": format_inr(risk.get('sla_breach_penalties_inr', 0))},
                        {"Exposure measure": "Total estimated exposure", "Amount": format_inr(risk.get('total_risk_exposure_inr', 0))},
                    ]
                    st.dataframe(risk_rows, hide_index=True, use_container_width=True)
                    st.caption("Gross margin is context only; it is not added again to unfulfilled revenue risk.")
                else:
                    st.info("The latest run did not produce an inventory impact observation.")

                st.markdown("#### Source comparison and decision")
                options = sourcing_result.get("options", [])
                order_details = dispatch_result.get("order_details", {})
                if options:
                    option_rows = []
                    for option in options:
                        on_time = option.get("transit_time_days", 999) <= impact_result.get("days_of_supply_remaining", 0)
                        full_cover = option.get("covers_full_deficit", False)
                        chosen = bool(order_details) and order_details.get("source") == option.get("source_id")
                        decision = "Selected" if chosen else "Safe alternative" if full_cover and on_time else "Partial capacity" if not full_cover else "Arrives after stockout"
                        option_rows.append({
                            "Source": option.get("source_name"),
                            "Type": option.get("source_type"),
                            "Available": option.get("available_surplus_units"),
                            "Proposed units": option.get("offered_quantity"),
                            "Case pack": option.get("pack_size_units", 1),
                            "Transit · business days": option.get("transit_time_days"),
                            "Route km": option.get("distance_km_estimate", "—"),
                            "Freight": format_inr(option.get('freight_cost_per_unit_inr', 0) * option.get('offered_quantity', 0)),
                            "Parts / rush cost": format_inr(option.get('purchase_cost_inr', 0)),
                            "Estimated total": format_inr(option.get('total_cost_inr', 0)),
                            "Reliability": f"{option['reliability_score']:.0%}" if option.get("reliability_score") is not None else "Internal hub",
                            "Decision": decision,
                        })
                    st.dataframe(option_rows, hide_index=True, use_container_width=True)
                    if order_details:
                        st.info(f"Order {order_details.get('order_id')} selected {order_details.get('source')} for {order_details.get('quantity')} units. ETA: {order_details.get('estimated_delivery_date')}; carrier: {order_details.get('freight_carrier')}.")
                elif impact_result.get("projected_stockout_units", 0) <= 0:
                    st.success("No replenishment source was needed for this incident.")
                else:
                    st.warning("No sourcing options were returned for this run.")

                if order_details:
                    st.markdown("#### Dispatch record")
                    st.json(order_details)
    with rail_col:
        st.markdown('<div class="panel-title">Active scenario</div>', unsafe_allow_html=True)
        st.markdown(f"**{st.session_state['scenario_name']}**")
        st.caption(f"{sku} · {destination} · {delay_days}-day delay")
        st.info("Change the incident configuration in Scenario Settings.")

elif page == "Inventory Network":
    sku_filter = st.selectbox("Product", ["All products", *PRODUCT_LABELS], key="network_sku_filter")
    hub_filter = st.selectbox("Warehouse", ["All warehouses", *ERP_DATABASE["warehouses"].keys()], key="network_hub_filter")
    selected_sku = None if sku_filter == "All products" else sku_filter.split(" · ", 1)[0]
    rows = []
    for wh_id, warehouse in ERP_DATABASE["warehouses"].items():
        if hub_filter != "All warehouses" and wh_id != hub_filter:
            continue
        for item_sku, stock in warehouse["stock"].items():
            if selected_sku and item_sku != selected_sku:
                continue
            free = stock["on_hand"] - stock["reserved"]
            rows.append({"Warehouse": warehouse["name"], "ID": wh_id, "SKU": item_sku, "On hand": stock["on_hand"], "Reserved": stock["reserved"], "Available": free, "Safety stock": stock.get("safety_stock_units", 0), "Reorder point": get_product_info(item_sku)["reorder_point_units"], "Daily demand": stock["daily_burn_rate"], "Days of supply": round(free / stock["daily_burn_rate"], 1)})
    st.dataframe(rows, hide_index=True, use_container_width=True)
    st.caption("Stock values update when a transfer order reserves inventory.")

elif page == "Transfer Orders":
    orders = list(reversed(ERP_DATABASE["transfer_orders"]))
    if orders:
        st.dataframe([{"Order": o["order_id"], "Incident": o.get("incident_id") or "—", "BOL": o.get("bill_of_lading", "—"), "Created": o["created_at"], "SKU": o["sku"], "Units": o["quantity"], "Source": o["source"], "Destination": o["destination"], "Carrier": o["freight_carrier"], "ETA": o["estimated_delivery_date"], "Status": o["status"], "Freight": format_inr(o['logistics_cost_inr']), "Total est. cost": format_inr(o.get('estimated_total_cost_inr', o['logistics_cost_inr']))} for o in orders], hide_index=True, use_container_width=True)
        selected_order = st.selectbox("Inspect order", [o["order_id"] for o in orders])
        st.json(next(o for o in orders if o["order_id"] == selected_order))
    else:
        st.info("No transfer orders yet. Run the autonomous agent from Disruption Overview to create one.")

elif page == "Replenishment Sources":
    st.subheader("Compare sources for a replenishment need")
    with st.form("source_assessment"):
        c1, c2, c3 = st.columns(3)
        source_sku_label = c1.selectbox("Product", PRODUCT_LABELS, key="source_sku")
        source_destination = c2.selectbox("Destination", list(ERP_DATABASE["warehouses"].keys()), key="source_destination")
        source_units = c3.number_input("Units needed", min_value=1, max_value=10000, value=200, key="source_units")
        source_clicked = st.form_submit_button("Find replenishment sources", type="primary")
    if source_clicked:
        source_sku = source_sku_label.split(" · ", 1)[0]
        source_result = json.loads(find_replenishment_options(source_sku, int(source_units), source_destination))
        st.session_state["source_result"] = source_result
    source_result = st.session_state.get("source_result")
    if source_result:
        source_rows = [{"Source": o["source_name"], "Qualification": o.get("qualification", "Internal network"), "Type": o["source_type"], "Surplus / capacity": o["available_surplus_units"], "Offered": o["offered_quantity"], "Case pack": o.get("pack_size_units", 1), "Lead time": f"{o['transit_time_days']} business days", "Carrier": o["carrier"], "Reliability": f"{o['reliability_score']:.0%}" if o.get("reliability_score") is not None else "—", "Estimated total": format_inr(o['total_cost_inr']), "Full coverage": o["covers_full_deficit"]} for o in source_result["options"]]
        st.dataframe(source_rows, hide_index=True, use_container_width=True)
        st.caption("Prices and availability are simulation estimates. The assessment does not reserve stock or place an order.")
    else:
        st.caption("Enter the required quantity and destination, then run the assessment to compare internal hubs and the qualified spot supplier.")

elif page == "Stockout Exposure":
    st.subheader("Calculate stockout exposure")
    with st.form("exposure_assessment"):
        c1, c2, c3 = st.columns(3)
        exposure_sku_label = c1.selectbox("Product", PRODUCT_LABELS, key="exposure_sku")
        exposure_destination = c2.selectbox("Destination", list(ERP_DATABASE["warehouses"].keys()), key="exposure_destination")
        exposure_delay = c3.number_input("Inbound delay (days)", min_value=0, max_value=60, value=12, key="exposure_delay")
        exposure_clicked = st.form_submit_button("Calculate exposure", type="primary")
    if exposure_clicked:
        exposure_sku = exposure_sku_label.split(" · ", 1)[0]
        exposure_result = json.loads(check_inventory_impact(exposure_sku, int(exposure_delay), exposure_destination))
        st.session_state["exposure_result"] = exposure_result
    exposure_result = st.session_state.get("exposure_result")
    if exposure_result:
        if "error" in exposure_result:
            st.error(exposure_result["error"])
        else:
            financial = exposure_result["financial_risk"]
            c1, c2, c3 = st.columns(3)
            c1.metric("Available units", exposure_result["current_available_units"])
            c2.metric("Days of supply", f"{exposure_result['days_of_supply_remaining']:.1f}")
            c3.metric("Projected deficit", f"{exposure_result['projected_stockout_units']} units")
            st.dataframe([{"Exposure component": "Unfulfilled revenue risk", "Amount": format_inr(financial['unfulfilled_revenue_risk_inr'])}, {"Exposure component": "Gross margin at risk · context only", "Amount": format_inr(financial['gross_margin_at_risk_inr'])}, {"Exposure component": "SLA breach penalties", "Amount": format_inr(financial['sla_breach_penalties_inr'])}, {"Exposure component": "Total estimated exposure", "Amount": format_inr(financial['total_risk_exposure_inr'])}], hide_index=True, use_container_width=True)
            st.caption("Gross margin is shown as context and is not added to the revenue exposure total.")

elif page == "Agent Activity":
    st.subheader("Periodic monitoring log")
    if st.session_state["monitor_history"]:
        st.dataframe(list(reversed(st.session_state["monitor_history"])), hide_index=True, use_container_width=True)
    else:
        st.caption("No periodic scans recorded in this session yet.")
    st.subheader("Agent run audit trail")
    activity = list(reversed(st.session_state["agent_activity"]))
    if not activity:
        st.info("No agent runs recorded yet. Run the autonomous triage from Disruption Overview to populate this audit trail.")
    for run_index, run in enumerate(activity, start=1):
        st.markdown(f"### Run {len(activity) - run_index + 1}")
        st.caption(run["prompt"])
        for event in run["events"]:
            kind = event.get("type")
            if kind == "thought":
                with st.expander(event.get("title", "Agent reasoning")):
                    st.write(event.get("content", ""))
            elif kind == "tool_call":
                with st.expander(f"Tool call · {event['tool_name']}"):
                    st.json(event.get("arguments", {}))
            elif kind == "tool_result":
                with st.expander(f"Tool result · {event['tool_name']}"):
                    st.json(event.get("result", {}))
            elif kind == "error":
                st.error(event.get("message", "Agent run failed."))
        if run.get("report"):
            st.success(f"{run['report']['status']} · {run['report']['executive_headline']}")

elif page == "Scenario Settings":
    st.subheader("Configure the default disruption")
    with st.form("scenario_settings"):
        scenario_names = list(ERP_DATABASE["scenarios"])
        scenario_name = st.selectbox("Disruption type", scenario_names, index=scenario_names.index(st.session_state["scenario_name"]) if st.session_state["scenario_name"] in scenario_names else 0)
        st.caption(ERP_DATABASE["scenarios"][scenario_name]["description"])
        st.caption("Primary affected hubs: " + ", ".join(ERP_DATABASE["scenarios"][scenario_name]["affected_hubs"]))
        scenario_prompt = st.text_input("Incident summary", value=st.session_state["scenario_prompt"])
        c1, c2, c3 = st.columns(3)
        scenario_sku_label = c1.selectbox("Product", PRODUCT_LABELS, index=list(ERP_DATABASE["products"]).index(st.session_state["scenario_sku"]))
        scenario_destination_label = c2.selectbox("Destination", [_warehouse_label(wh_id) for wh_id in ERP_DATABASE["warehouses"]], index=list(ERP_DATABASE["warehouses"]).index(st.session_state["scenario_destination"]))
        scenario_delay = c3.number_input("Inbound delay (days)", min_value=0, max_value=60, value=int(st.session_state["scenario_delay"]))
        scenario_incident_id = st.text_input("Incident ID · duplicate-order key", value=st.session_state["scenario_incident_id"], help="Use a unique ID for each new disruption. Reusing an ID prevents a second order for that incident.")
        monitor_enabled = st.toggle("Enable periodic monitoring and simulated auto-orders", value=st.session_state["monitor_enabled"])
        monitor_interval = st.select_slider("Scan interval", options=[15, 30, 60, 120, 300], value=st.session_state["monitor_interval_seconds"], format_func=lambda seconds: f"{seconds} sec" if seconds < 60 else f"{seconds // 60} min")
        st.caption("While enabled, the app rechecks this incident at the selected interval and dispatches a simulated order only when full coverage can arrive before projected stockout. Monitoring runs only while this Streamlit session stays open; it is not a background service. Disable monitoring to stop scans.")
        saved = st.form_submit_button("Save scenario settings", type="primary")
    if saved:
        if monitor_enabled and not scenario_incident_id.strip():
            st.error("Incident ID cannot be blank while the monitor is enabled.")
        else:
            st.session_state["scenario_name"] = scenario_name
            st.session_state["scenario_prompt"] = scenario_prompt
            st.session_state["scenario_sku"] = scenario_sku_label.split(" · ", 1)[0]
            st.session_state["scenario_destination"] = scenario_destination_label.split(" · ", 1)[0]
            st.session_state["scenario_delay"] = int(scenario_delay)
            st.session_state["scenario_incident_id"] = scenario_incident_id.strip()
            st.session_state["monitor_enabled"] = monitor_enabled
            st.session_state["monitor_interval_seconds"] = int(monitor_interval)
            st.success("Scenario and monitor settings saved.")
            st.rerun()

st.markdown('<div class="footnote" style="text-align:center;padding-top:1rem">Nexus Ops India workspace · Simulated Indian supply chain and INR inventory data · ERP actions are demo-only</div>', unsafe_allow_html=True)
