# File: app/services/projector.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Ratios:
    """All ratios must be > 0. Units:
    - doors_per_appt: doors / appointment
    - appts_per_deal: appointments / signed deal
    - avg_rcv_per_completed_deal: dollars / completed deal
    """
    doors_per_appt: float
    appts_per_deal: float
    avg_rcv_per_completed_deal: float

def _eff_rate(commission_pct: float, company_margin_pct: float, base: str) -> float:
    """Return effective commission on revenue as a decimal (e.g., 0.12)."""
    b = (base or "").strip().lower()
    if b == "profit":
        return (commission_pct/100.0) * (company_margin_pct/100.0)
    if b == "revenue":
        return commission_pct/100.0
    raise ValueError("Invalid commission base")

def projector_metrics(
    annual_goal: float,
    days: int,
    ratios: Ratios,
    commission_pct: float,
    company_margin_pct: float,
    commission_base: str,   # 'profit' | 'revenue'
) -> dict:
    if days <= 0:
        raise ValueError("Days must be > 0")
    if ratios.doors_per_appt <= 0 or ratios.appts_per_deal <= 0:
        raise ValueError("Historical ratios must be > 0")
    if ratios.avg_rcv_per_completed_deal <= 0:
        raise ValueError("Average RCV must be > 0")
    if not (0 <= commission_pct <= 100 and 0 <= company_margin_pct <= 100):
        raise ValueError("Percents must be between 0 and 100")

    eff = _eff_rate(commission_pct, company_margin_pct, commission_base)
    avg_comm_per_deal = ratios.avg_rcv_per_completed_deal * eff

    daily_income   = annual_goal / float(days)
    deals_per_day  = daily_income / avg_comm_per_deal
    appts_per_day  = deals_per_day * ratios.appts_per_deal
    doors_per_day  = appts_per_day * ratios.doors_per_appt

    return {
        "eff_rate": eff,  # decimal
        "avg_comm_per_deal": avg_comm_per_deal,
        "deals_per_day": deals_per_day,
        "appts_per_day": appts_per_day,
        "doors_per_day": doors_per_day,
    }
