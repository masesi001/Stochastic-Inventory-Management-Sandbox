"""Conservation of mass: initial + received - sold = ending."""
import os, sys, tempfile, sqlite3
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SimConfig
from db.logger import DBLogger
from engine.simulation import InventorySimulation

def test_mass_balance():
    db_path = os.path.join(tempfile.gettempdir(), "test_mass.db")
    if os.path.exists(db_path): os.remove(db_path)
    cfg = SimConfig(horizon_days=200, seed=7)
    db = DBLogger(db_path)
    sim = InventorySimulation(cfg, db=db)
    initial = sim.on_hand
    res = sim.run()
    db.close()

    conn = sqlite3.connect(db_path)
    received = conn.execute(
        "SELECT COALESCE(SUM(qty),0) FROM orders WHERE run_id=? AND arrival_day < ?",
        (res.run_id, cfg.horizon_days)).fetchone()[0]
    in_transit_remaining = conn.execute(
        "SELECT COALESCE(SUM(qty),0) FROM orders WHERE run_id=? AND arrival_day >= ?",
        (res.run_id, cfg.horizon_days)).fetchone()[0]
    conn.close()

    # initial + received - sold == ending on-hand
    assert initial + received - res.total_sold == res.end_on_hand, (
        initial, received, res.total_sold, res.end_on_hand, in_transit_remaining)
