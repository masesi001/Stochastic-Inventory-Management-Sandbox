import math, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.eoq import eoq, total_annual_cost, safety_stock, reorder_point

def test_eoq_textbook():
    # D=1000/yr, K=10, H=2 -> Q*=100
    Q = eoq(daily_lambda=1000/365, ordering_cost=10, holding_cost=2)
    assert math.isclose(Q, 100.0, rel_tol=1e-6)

def test_total_cost_minimum_at_eoq():
    lam = 1000/365
    Q = eoq(lam, 10, 2)
    tc = total_annual_cost(Q, lam, 10, 2)
    # Perturb +/- 10%
    assert total_annual_cost(Q*0.9, lam, 10, 2) >= tc
    assert total_annual_cost(Q*1.1, lam, 10, 2) >= tc

def test_safety_stock_zero_when_no_variance():
    assert safety_stock(1.65, 10, 0, 5, 0) == 0.0

def test_rop_basic():
    assert reorder_point(10, 5, 7) == 57
