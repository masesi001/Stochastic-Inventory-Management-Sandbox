"""Deterministic benchmark: with σ=0 the simulated annual ordering+holding cost
should match analytic EOQ TC within 2%."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SimConfig
from engine.simulation import InventorySimulation
from models.eoq import eoq, total_annual_cost

def test_deterministic_within_2pct():
    cfg = SimConfig(
        daily_demand_lambda=20.0,
        lead_time_mean=5.0, lead_time_std=0.0,
        ordering_cost=400.0, holding_cost=10.0,
        demand_std_override=0.0,
        horizon_days=365, seed=1,
    )
    res = InventorySimulation(cfg, deterministic=True).run()
    Q_star = eoq(cfg.daily_demand_lambda, cfg.ordering_cost, cfg.holding_cost)
    tc_analytic = total_annual_cost(Q_star, cfg.daily_demand_lambda,
                                    cfg.ordering_cost, cfg.holding_cost)
    sim_tc = res.total_ordering_cost + res.total_holding_cost
    variance = abs(sim_tc - tc_analytic) / tc_analytic
    assert variance < 0.02, f"variance {variance:.4f} >= 2% (sim={sim_tc:.2f}, eoq={tc_analytic:.2f})"
