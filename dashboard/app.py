"""Streamlit dashboard.
Run: streamlit run dashboard/app.py
"""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from dataclasses import replace
from config import SimConfig
from engine.simulation import InventorySimulation
from db.logger import DBLogger
from analysis.sawtooth import plot_sawtooth, load_events
from analysis.sensitivity import sweep_lead_time_sigma

st.set_page_config(page_title="Stochastic Inventory Sandbox", layout="wide")
st.title("Stochastic Inventory Management — Sandbox")

with st.sidebar:
    st.header("Parameters")
    lam = st.slider("Daily demand λ (units)", 1.0, 100.0, 25.0, 1.0)
    mu_L = st.slider("Lead time mean μ_L (days)", 1.0, 30.0, 7.0, 0.5)
    sg_L = st.slider("Lead time σ_L (days)", 0.0, 10.0, 1.5, 0.1)
    K   = st.slider("Ordering cost K (KES)", 50.0, 5000.0, 500.0, 50.0)
    H   = st.slider("Holding cost H (KES/unit/yr)", 1.0, 200.0, 12.0, 1.0)
    price = st.slider("Selling price (KES)", 10.0, 1000.0, 160.0, 5.0)
    horizon = st.slider("Horizon (days)", 30, 1095, 365, 30)
    seed = st.number_input("Seed", value=42, step=1)
    run_btn = st.button("Run simulation", type="primary")

if run_btn:
    cfg = SimConfig(daily_demand_lambda=lam, lead_time_mean=mu_L, lead_time_std=sg_L,
                    ordering_cost=K, holding_cost=H, price=price,
                    horizon_days=horizon, seed=int(seed))
    db_path = os.path.join(tempfile.gettempdir(), "dashboard_sim.db")
    if os.path.exists(db_path): os.remove(db_path)
    db = DBLogger(db_path)
    res = InventorySimulation(cfg, db=db).run()
    db.close()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("EOQ Q*", f"{res.Q:,.0f}")
    c2.metric("ROP", f"{res.ROP:,.1f}")
    c3.metric("Fill rate", f"{res.fill_rate*100:.2f}%")
    c4.metric("Total cost (KES)", f"{res.total_cost:,.0f}")

    img = plot_sawtooth(db_path, res.run_id, res.ROP,
                        out_path=os.path.join(tempfile.gettempdir(), "sawtooth.png"))
    st.image(img, caption="Sawtooth diagram")

    st.subheader("Daily event log (head)")
    st.dataframe(load_events(db_path, res.run_id).head(50))

    with st.expander("Sensitivity sweep over lead-time σ"):
        df = sweep_lead_time_sigma(cfg, sigmas=[0.0, 1.0, 2.0, 4.0], replications=10)
        st.dataframe(df.groupby("lead_time_sigma").mean(numeric_only=True))
