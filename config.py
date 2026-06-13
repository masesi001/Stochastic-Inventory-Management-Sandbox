"""Central simulation parameters."""
from dataclasses import dataclass, field, asdict
import json

@dataclass
class SimConfig:
    # Product economics
    product_id: int = 1
    product_name: str = "Maize Flour 2kg"
    unit_cost: float = 120.0          # KES per unit
    price: float = 160.0              # selling price per unit
    ordering_cost: float = 500.0      # K — fixed cost per order
    holding_cost: float = 12.0        # H — per unit per year

    # Stochastic demand
    daily_demand_lambda: float = 25.0  # Poisson λ (units/day)

    # Stochastic lead time (days)
    lead_time_mean: float = 7.0        # μ_L
    lead_time_std: float = 1.5         # σ_L  (set to 0 for deterministic benchmark)

    # Demand std override (None => sqrt(λ) per Poisson). Set 0 for deterministic.
    demand_std_override: float | None = None

    # Service level z-score
    service_z: float = 1.65            # ~95%

    # Simulation horizon
    horizon_days: int = 365
    initial_stock: int | None = None   # None => starts at EOQ
    seed: int = 42

    def to_json(self) -> str:
        return json.dumps(asdict(self))
