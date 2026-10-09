"""Production-impact layer and daily material simulation.

Implements Sections 11 & 12 of the VendorGuard AI Blueprint:
- Available stock & coverage days
- Replenishment arrival lead time & scenario gap days
- Daily inventory trajectory simulation: B[d] = B[d-1] + usable_receipts[d] - required_consumption[d]
- Base vs stress delayed scenario
- Lexicographical prioritization (urgency -> criticality -> substitution -> risk score)
"""

from datetime import date, timedelta
from typing import List, Dict, Optional, Tuple
from .models_domain import (
    MaterialCriticality,
    DailyInventoryPoint,
    MaterialExposureResult,
)


def calculate_coverage(
    on_hand: float,
    reserved: float,
    daily_consumption: float,
) -> Tuple[float, float]:
    """Calculates available stock and days of coverage.

    Returns:
        (available_stock, coverage_days)
    """
    available_stock = max(0.0, on_hand - reserved)
    if daily_consumption <= 0.0:
        coverage_days = 999.0  # Infinite / zero demand
    else:
        coverage_days = available_stock / daily_consumption
    return round(available_stock, 2), round(coverage_days, 2)


def calculate_scenario_gap(
    coverage_days: float,
    scenario_arrival_lead_time: float,
) -> float:
    """Calculates scenario supply gap in days."""
    gap = max(0.0, scenario_arrival_lead_time - coverage_days)
    return round(gap, 2)


def simulate_inventory_trajectory(
    start_date: date,
    initial_available_stock: float,
    daily_consumption: float,
    scheduled_receipts_by_date: Dict[date, float],
    horizon_days: int = 30,
) -> Tuple[List[DailyInventoryPoint], Optional[int]]:
    """Simulates daily stock balance B[d] = B[d-1] + receipts[d] - consumption[d].

    Returns:
        (trajectory_points, first_stockout_day_number)
    """
    trajectory: List[DailyInventoryPoint] = []
    current_balance = initial_available_stock
    first_stockout_day: Optional[int] = None

    for day_idx in range(1, horizon_days + 1):
        sim_date = start_date + timedelta(days=day_idx)
        starting_bal = current_balance
        receipts_today = scheduled_receipts_by_date.get(sim_date, 0.0)
        consumption_today = daily_consumption

        ending_bal = starting_bal + receipts_today - consumption_today

        is_stockout = ending_bal < 0.0
        if is_stockout and first_stockout_day is None:
            first_stockout_day = day_idx

        trajectory.append(
            DailyInventoryPoint(
                day=day_idx,
                date_str=sim_date.isoformat(),
                starting_balance=round(starting_bal, 2),
                scheduled_receipts=round(receipts_today, 2),
                required_consumption=round(consumption_today, 2),
                ending_balance=round(ending_bal, 2),
                is_stockout=is_stockout,
            )
        )
        current_balance = ending_bal

    return trajectory, first_stockout_day


def evaluate_material_exposure(
    material_id: str,
    material_name: str,
    criticality: MaterialCriticality,
    unit: str,
    on_hand_stock: float,
    reserved_stock: float,
    daily_consumption: float,
    start_date: date,
    normal_receipts_by_date: Dict[date, float],
    normal_lead_time_days: float,
    stress_delay_days: float = 6.0,
    alternate_suppliers_count: int = 0,
    horizon_days: int = 30,
) -> MaterialExposureResult:
    """Evaluates material coverage, scenario gap, and base vs stress simulation trajectories."""
    available_stock, coverage_days = calculate_coverage(
        on_hand=on_hand_stock,
        reserved=reserved_stock,
        daily_consumption=daily_consumption,
    )

    scenario_arrival_days = normal_lead_time_days + stress_delay_days
    scenario_gap_days = calculate_scenario_gap(
        coverage_days=coverage_days,
        scenario_arrival_lead_time=scenario_arrival_days,
    )

    # Base trajectory
    traj_base, _ = simulate_inventory_trajectory(
        start_date=start_date,
        initial_available_stock=available_stock,
        daily_consumption=daily_consumption,
        scheduled_receipts_by_date=normal_receipts_by_date,
        horizon_days=horizon_days,
    )

    # Stress trajectory: shift receipts forward by stress_delay_days
    stress_receipts: Dict[date, float] = {}
    for d, qty in normal_receipts_by_date.items():
        delayed_d = d + timedelta(days=int(stress_delay_days))
        stress_receipts[delayed_d] = stress_receipts.get(delayed_d, 0.0) + qty

    traj_stress, stockout_day = simulate_inventory_trajectory(
        start_date=start_date,
        initial_available_stock=available_stock,
        daily_consumption=daily_consumption,
        scheduled_receipts_by_date=stress_receipts,
        horizon_days=horizon_days,
    )

    return MaterialExposureResult(
        material_id=material_id,
        material_name=material_name,
        criticality=criticality,
        on_hand_stock=on_hand_stock,
        reserved_stock=reserved_stock,
        available_stock=available_stock,
        unit=unit,
        daily_consumption=daily_consumption,
        coverage_days=coverage_days,
        scenario_arrival_days=scenario_arrival_days,
        scenario_gap_days=scenario_gap_days,
        day_to_stockout=stockout_day,
        trajectory_base=traj_base,
        trajectory_stress=traj_stress,
        has_alternate_supplier=alternate_suppliers_count > 0,
        alternate_suppliers_count=alternate_suppliers_count,
    )


def rank_priority_key(
    exposure: MaterialExposureResult,
    supplier_risk_score: Optional[float],
) -> Tuple[int, int, int, float]:
    """Computes a lexicographical sort key for triage prioritization.

    Sort order:
      1. Shortage urgency: day_to_stockout (None -> 999)
      2. Material criticality: Tier 1 (0) > Tier 2 (1) > Tier 3 (2)
      3. Substitution constraint: single source (0) > has alternate (1)
      4. Risk score: descending (-risk_score)
    """
    # 1. Stockout urgency (lower day number = higher priority)
    urgency = exposure.day_to_stockout if exposure.day_to_stockout is not None else 999

    # 2. Criticality
    crit_map = {
        MaterialCriticality.TIER_1: 0,
        MaterialCriticality.TIER_2: 1,
        MaterialCriticality.TIER_3: 2,
    }
    crit_val = crit_map.get(exposure.criticality, 2)

    # 3. Substitution (single-source is more dangerous)
    sub_val = 0 if not exposure.has_alternate_supplier else 1

    # 4. Supplier score (inverted so descending order works in min sort)
    risk_val = -(supplier_risk_score if supplier_risk_score is not None else 0.0)

    return (urgency, crit_val, sub_val, risk_val)
