"""EOQ / ROP / Safety Stock formulas."""
from __future__ import annotations
import math

def annual_demand(daily_lambda: float) -> float:
    return daily_lambda * 365.0

def eoq(daily_lambda: float, ordering_cost: float, holding_cost: float) -> float:
    """Q* = sqrt(2 D K / H)."""
    D = annual_demand(daily_lambda)
    return math.sqrt(2.0 * D * ordering_cost / holding_cost)

def total_annual_cost(Q: float, daily_lambda: float, K: float, H: float) -> float:
    """TC(Q) = (D/Q)*K + (Q/2)*H — textbook EOQ cost."""
    D = annual_demand(daily_lambda)
    return (D / Q) * K + (Q / 2.0) * H

def safety_stock(z: float, mu_d: float, sigma_d: float, mu_L: float, sigma_L: float) -> float:
    """SS = z * sqrt(μ_L * σ_d² + μ_d² * σ_L²)."""
    return z * math.sqrt(mu_L * sigma_d ** 2 + mu_d ** 2 * sigma_L ** 2)

def reorder_point(mu_d: float, mu_L: float, ss: float) -> float:
    """ROP = μ_d * μ_L + SS."""
    return mu_d * mu_L + ss
