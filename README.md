# Stochastic Inventory Management Simulation System

Reference implementation for the BSc proposal:
*A Program to Design and Implement a Stochastic Inventory Management Simulation System Using SimPy and Python.*

## Features

- **EOQ + ROP** mathematical core with safety-stock formula (`models/eoq.py`).
- **Discrete Event Simulation engine** using SimPy with Poisson demand and Gaussian lead times (`engine/simulation.py`).
- **SQLite persistence** in 3NF (`db/schema.sql`) — products, simulation_runs, daily_events, orders, stockouts.
- **Sawtooth visualization** with Matplotlib (`analysis/sawtooth.py`).
- **Streamlit dashboard** with sensitivity sliders (`dashboard/app.py`).
- **V&V test suite** including:
  - EOQ formula correctness
  - Conservation of mass (initial + received − sold = ending)
  - Deterministic benchmark (<2% variance vs. analytic EOQ TC)

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Run the demo simulation

```bash
python run_demo.py        # produces inventory_sim.db + sawtooth.png
```

## Run the test suite (V&V)

```bash
pytest -q
```

All three tests must pass — the benchmark test enforces the <2% variance requirement from the proposal.

## Launch the dashboard

```bash
streamlit run dashboard/app.py
```

Move the sliders for λ, μ_L, σ_L, K, H and observe sawtooth + KPIs update in real time.

## File map

| Path | Purpose |
|------|---------|
| `config.py` | `SimConfig` dataclass — all simulation parameters |
| `models/eoq.py` | EOQ, safety stock, ROP formulas |
| `models/distributions.py` | Poisson / Gaussian samplers (seeded) |
| `db/schema.sql` | 3NF SQLite schema |
| `db/logger.py` | Insert helpers + run lifecycle |
| `engine/simulation.py` | SimPy DES engine |
| `analysis/sawtooth.py` | Matplotlib sawtooth diagram |
| `analysis/sensitivity.py` | Monte-Carlo lead-time sweep |
| `dashboard/app.py` | Streamlit UI |
| `tests/` | pytest V&V suite |
| `data/sample_products.csv` | 5 SKUs of sample SME inventory |
| `data/sample_run_seed.json` | Reproducible seed configuration |
