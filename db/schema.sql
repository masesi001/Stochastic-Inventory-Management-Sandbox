-- 3NF schema for the Stochastic Inventory Simulation
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS products (
    product_id     INTEGER PRIMARY KEY,
    name           TEXT    NOT NULL UNIQUE,
    unit_cost      REAL    NOT NULL,
    price          REAL    NOT NULL,
    ordering_cost  REAL    NOT NULL,
    holding_cost   REAL    NOT NULL
);

CREATE TABLE IF NOT EXISTS simulation_runs (
    run_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id  INTEGER NOT NULL REFERENCES products(product_id),
    started_at  TEXT    NOT NULL,
    seed        INTEGER NOT NULL,
    horizon     INTEGER NOT NULL,
    params_json TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS daily_events (
    event_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id      INTEGER NOT NULL REFERENCES simulation_runs(run_id) ON DELETE CASCADE,
    day         INTEGER NOT NULL,
    demand      INTEGER NOT NULL,
    sold        INTEGER NOT NULL,
    on_hand     INTEGER NOT NULL,
    in_transit  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id      INTEGER NOT NULL REFERENCES simulation_runs(run_id) ON DELETE CASCADE,
    placed_day  INTEGER NOT NULL,
    arrival_day INTEGER NOT NULL,
    qty         INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS stockouts (
    stockout_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id       INTEGER NOT NULL REFERENCES simulation_runs(run_id) ON DELETE CASCADE,
    day          INTEGER NOT NULL,
    shortfall    INTEGER NOT NULL,
    lost_revenue REAL    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_events_run_day ON daily_events(run_id, day);
CREATE INDEX IF NOT EXISTS idx_orders_run     ON orders(run_id);
CREATE INDEX IF NOT EXISTS idx_stockouts_run  ON stockouts(run_id);
