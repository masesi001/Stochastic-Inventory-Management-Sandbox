"""SQLite logger for simulation events."""
from __future__ import annotations
import sqlite3, os, datetime as dt
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent / "schema.sql"

class DBLogger:
    def __init__(self, db_path: str = "inventory_sim.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()
        self.run_id: int | None = None

    def _init_schema(self):
        with open(SCHEMA_PATH) as f:
            self.conn.executescript(f.read())
        self.conn.commit()

    def upsert_product(self, p) -> int:
        cur = self.conn.execute(
            """INSERT INTO products(product_id,name,unit_cost,price,ordering_cost,holding_cost)
               VALUES(?,?,?,?,?,?)
               ON CONFLICT(product_id) DO UPDATE SET
                 name=excluded.name, unit_cost=excluded.unit_cost, price=excluded.price,
                 ordering_cost=excluded.ordering_cost, holding_cost=excluded.holding_cost""",
            (p.product_id, p.product_name, p.unit_cost, p.price, p.ordering_cost, p.holding_cost),
        )
        self.conn.commit()
        return p.product_id

    def start_run(self, cfg) -> int:
        self.upsert_product(cfg)
        cur = self.conn.execute(
            "INSERT INTO simulation_runs(product_id,started_at,seed,horizon,params_json) VALUES(?,?,?,?,?)",
            (cfg.product_id, dt.datetime.utcnow().isoformat(), cfg.seed, cfg.horizon_days, cfg.to_json()),
        )
        self.conn.commit()
        self.run_id = cur.lastrowid
        return self.run_id

    def log_day(self, day, demand, sold, on_hand, in_transit):
        self.conn.execute(
            "INSERT INTO daily_events(run_id,day,demand,sold,on_hand,in_transit) VALUES(?,?,?,?,?,?)",
            (self.run_id, day, demand, sold, on_hand, in_transit),
        )

    def log_order(self, placed_day, arrival_day, qty):
        self.conn.execute(
            "INSERT INTO orders(run_id,placed_day,arrival_day,qty) VALUES(?,?,?,?)",
            (self.run_id, placed_day, arrival_day, qty),
        )

    def log_stockout(self, day, shortfall, lost_revenue):
        self.conn.execute(
            "INSERT INTO stockouts(run_id,day,shortfall,lost_revenue) VALUES(?,?,?,?)",
            (self.run_id, day, shortfall, lost_revenue),
        )

    def commit(self): self.conn.commit()
    def close(self): self.conn.commit(); self.conn.close()
