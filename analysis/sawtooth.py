"""Sawtooth diagram + KPIs from event log."""
from __future__ import annotations
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

def load_events(db_path: str, run_id: int) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(
        "SELECT day, demand, sold, on_hand, in_transit FROM daily_events "
        "WHERE run_id=? ORDER BY day", conn, params=(run_id,))
    conn.close()
    return df

def load_orders(db_path, run_id):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(
        "SELECT placed_day, arrival_day, qty FROM orders WHERE run_id=?",
        conn, params=(run_id,))
    conn.close()
    return df

def plot_sawtooth(db_path: str, run_id: int, rop: float, out_path: str = "sawtooth.png"):
    df = load_events(db_path, run_id)
    orders = load_orders(db_path, run_id)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df["day"], df["on_hand"], lw=1.2, color="#1f77b4", label="On-hand stock")
    ax.axhline(rop, color="#d62728", ls="--", lw=1, label=f"ROP = {rop:.1f}")
    for _, o in orders.iterrows():
        ax.axvline(o["arrival_day"], color="#2ca02c", alpha=0.25, lw=0.8)
    ax.set_xlabel("Day"); ax.set_ylabel("Units on hand")
    ax.set_title(f"Inventory Sawtooth — Run {run_id}")
    ax.legend(loc="upper right"); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return out_path
