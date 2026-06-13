"""SimPy Discrete Event Simulation engine."""
from __future__ import annotations
import math, simpy
import numpy as np
from dataclasses import dataclass, field

from config import SimConfig
from models.distributions import Distributions
from models.eoq import eoq, safety_stock, reorder_point
from db.logger import DBLogger


@dataclass
class RunResult:
    run_id: int
    Q: float
    ROP: float
    SS: float
    total_demand: int
    total_sold: int
    total_stockouts: int
    total_lost_revenue: float
    total_ordering_cost: float
    total_holding_cost: float
    total_purchase_cost: float
    total_cost: float
    fill_rate: float
    end_on_hand: int


class InventorySimulation:
    def __init__(self, cfg: SimConfig, db: DBLogger | None = None,
                 deterministic: bool = False):
        self.cfg = cfg
        self.deterministic = deterministic
        self.db = db
        self.dist = Distributions(seed=cfg.seed)

        # Demand stats for ROP
        sigma_d = (cfg.demand_std_override
                   if cfg.demand_std_override is not None
                   else math.sqrt(cfg.daily_demand_lambda))
        if deterministic:
            sigma_d = 0.0
            cfg.lead_time_std = 0.0

        self.Q = eoq(cfg.daily_demand_lambda, cfg.ordering_cost, cfg.holding_cost)
        self.SS = safety_stock(cfg.service_z, cfg.daily_demand_lambda, sigma_d,
                               cfg.lead_time_mean, cfg.lead_time_std)
        if deterministic:
            self.SS = 0.0
        self.ROP = reorder_point(cfg.daily_demand_lambda, cfg.lead_time_mean, self.SS)

        self.on_hand = int(cfg.initial_stock if cfg.initial_stock is not None
                           else round(self.Q))
        self.in_transit = 0

        # Accumulators
        self.total_demand = 0
        self.total_sold = 0
        self.total_stockouts = 0
        self.total_lost_revenue = 0.0
        self.num_orders = 0
        self.holding_cost_accum = 0.0  # per-day holding accumulation

    # ---------- SimPy processes ----------
    def daily_loop(self, env: simpy.Environment):
        cfg = self.cfg
        H_per_day = cfg.holding_cost / 365.0
        while True:
            day = int(env.now)
            demand = self.dist.demand(cfg.daily_demand_lambda, self.deterministic)
            sold = min(self.on_hand, demand)
            self.on_hand -= sold
            self.total_demand += demand
            self.total_sold += sold

            if demand > sold:
                shortfall = demand - sold
                lost_rev = shortfall * cfg.price
                self.total_stockouts += shortfall
                self.total_lost_revenue += lost_rev
                if self.db: self.db.log_stockout(day, shortfall, lost_rev)

            # Holding cost on end-of-day stock
            self.holding_cost_accum += self.on_hand * H_per_day

            # Replenishment trigger
            if (self.on_hand + self.in_transit) <= self.ROP:
                env.process(self.replenish(env, day))

            if self.db: self.db.log_day(day, demand, sold, self.on_hand, self.in_transit)
            yield env.timeout(1)

    def replenish(self, env, placed_day):
        cfg = self.cfg
        qty = int(round(self.Q))
        self.in_transit += qty
        self.num_orders += 1
        lt = self.dist.lead_time(cfg.lead_time_mean, cfg.lead_time_std)
        if self.db: self.db.log_order(placed_day, int(placed_day + lt), qty)
        yield env.timeout(lt)
        self.in_transit -= qty
        self.on_hand += qty

    # ---------- Run ----------
    def run(self) -> RunResult:
        cfg = self.cfg
        if self.db: self.db.start_run(cfg)
        env = simpy.Environment()
        env.process(self.daily_loop(env))
        env.run(until=cfg.horizon_days)
        if self.db: self.db.commit()

        ordering_cost_total = self.num_orders * cfg.ordering_cost
        purchase_cost_total = self.num_orders * int(round(self.Q)) * cfg.unit_cost
        total_cost = ordering_cost_total + self.holding_cost_accum + purchase_cost_total
        fill_rate = (self.total_sold / self.total_demand) if self.total_demand else 1.0

        return RunResult(
            run_id=self.db.run_id if self.db else -1,
            Q=self.Q, ROP=self.ROP, SS=self.SS,
            total_demand=self.total_demand, total_sold=self.total_sold,
            total_stockouts=self.total_stockouts,
            total_lost_revenue=self.total_lost_revenue,
            total_ordering_cost=ordering_cost_total,
            total_holding_cost=self.holding_cost_accum,
            total_purchase_cost=purchase_cost_total,
            total_cost=total_cost,
            fill_rate=fill_rate,
            end_on_hand=self.on_hand,
        )
