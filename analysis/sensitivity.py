"""Monte-Carlo sensitivity sweep over lead-time variance."""
from __future__ import annotations
import numpy as np, pandas as pd
from copy import replace as _r  # not standard; use dataclasses.replace
from dataclasses import replace
from config import SimConfig
from engine.simulation import InventorySimulation

def sweep_lead_time_sigma(base: SimConfig, sigmas, replications: int = 20) -> pd.DataFrame:
    rows = []
    for sigma in sigmas:
        for r in range(replications):
            cfg = replace(base, lead_time_std=sigma, seed=base.seed + r)
            res = InventorySimulation(cfg).run()
            rows.append({
                "lead_time_sigma": sigma,
                "rep": r,
                "total_cost": res.total_cost,
                "stockouts": res.total_stockouts,
                "fill_rate": res.fill_rate,
            })
    return pd.DataFrame(rows)
