# File: tests/test_projector.py
import math
from app.services.projector import Ratios, projector_metrics

def test_profit_base_effective_rate_and_outputs():
    ratios = Ratios(
        doors_per_appt=5.0,                 # 10 doors / 2 appts
        appts_per_deal=2.0,                 # 2 appts / deal
        avg_rcv_per_completed_deal=20000.0, # $20k per completed deal
    )
    m = projector_metrics(
        annual_goal=120000.0, days=240,
        ratios=ratios,
        commission_pct=40.0, company_margin_pct=30.0,
        commission_base="profit",
    )
    assert math.isclose(m["eff_rate"], 0.12, rel_tol=1e-9)
    assert math.isclose(m["avg_comm_per_deal"], 2400.0, rel_tol=1e-9)
    assert math.isclose(m["deals_per_day"], (120000/240)/2400, rel_tol=1e-9)
    assert math.isclose(m["appts_per_day"], ((120000/240)/2400)*2, rel_tol=1e-9)
    assert math.isclose(m["doors_per_day"], ((120000/240)/2400)*2*5, rel_tol=1e-9)

def test_revenue_base_effective_rate_and_outputs():
    ratios = Ratios(doors_per_appt=4.0, appts_per_deal=1.5, avg_rcv_per_completed_deal=15000.0)
    m = projector_metrics(
        annual_goal=150000.0, days=250,
        ratios=ratios,
        commission_pct=10.0, company_margin_pct=0.0,
        commission_base="revenue",
    )
    assert math.isclose(m["eff_rate"], 0.10, rel_tol=1e-9)
    assert math.isclose(m["avg_comm_per_deal"], 1500.0, rel_tol=1e-9)
