"""End-to-end demo: run a single simulation, log to SQLite, render sawtooth."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import SimConfig
from db.logger import DBLogger
from engine.simulation import InventorySimulation
from analysis.sawtooth import plot_sawtooth

if __name__ == "__main__":
    cfg = SimConfig()
    db_path = "inventory_sim.db"
    if os.path.exists(db_path): os.remove(db_path)
    db = DBLogger(db_path)
    res = InventorySimulation(cfg, db=db).run()
    db.close()

    print(f"Run #{res.run_id}")
    print(f"  EOQ Q*           = {res.Q:.2f}")
    print(f"  Safety stock SS  = {res.SS:.2f}")
    print(f"  Reorder point    = {res.ROP:.2f}")
    print(f"  Total demand     = {res.total_demand}")
    print(f"  Total sold       = {res.total_sold}")
    print(f"  Stockout units   = {res.total_stockouts}")
    print(f"  Lost revenue     = KES {res.total_lost_revenue:,.2f}")
    print(f"  Ordering cost    = KES {res.total_ordering_cost:,.2f}")
    print(f"  Holding cost     = KES {res.total_holding_cost:,.2f}")
    print(f"  Fill rate        = {res.fill_rate*100:.2f}%")

    plot_sawtooth(db_path, res.run_id, res.ROP, "sawtooth.png")
    print("  Sawtooth chart -> sawtooth.png")
