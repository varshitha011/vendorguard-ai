"""Operational indicators and pattern detection module.

Implements Sections 8 & 10 of the VendorGuard AI Blueprint:
- On-time fulfillment rate & Late fraction (L)
- Delay factor (D) with 10-day scaling
- Trend deterioration factor (T) comparing current vs prior 30-day windows with 5-day scaling
- Fulfillment shortfall (F)
- Cold-start sufficiency rules
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
import numpy as np

from .models_domain import (
    OrderLineRecord,
    ReceiptRecord,
    OperationalMetrics,
    SufficiencyState,
)


def clip(val: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    return max(min_val, min(max_val, val))


def compute_order_line_delay(
    order_line: OrderLineRecord,
    receipts: List[ReceiptRecord],
    cutoff_date: date,
    required_fulfillment_fraction: float = 1.0,
    grace_days: int = 0,
) -> Tuple[bool, bool, Optional[float], float]:
    """Computes delay metrics for a single purchase order line.

    Returns:
        (is_fulfilled_on_time, is_completed, completed_delay_days, current_shortfall)
    """
    due_date = order_line.committed_due_date
    grace_due_date = due_date + timedelta(days=grace_days)
    target_qty = required_fulfillment_fraction * order_line.ordered_quantity

    # Filter receipts known/recorded by cutoff
    valid_receipts = [
        r for r in receipts
        if r.po_line_id == order_line.id and r.received_at.date() <= cutoff_date
    ]
    # Sort by received_at timestamp
    valid_receipts.sort(key=lambda r: r.received_at)

    total_accepted_by_due = 0.0
    total_accepted_at_cutoff = 0.0
    completion_date: Optional[date] = None

    running_accepted = 0.0
    for r in valid_receipts:
        running_accepted += r.accepted_quantity
        if r.received_at.date() <= grace_due_date:
            total_accepted_by_due += r.accepted_quantity
        if running_accepted >= target_qty and completion_date is None:
            completion_date = r.received_at.date()

    total_accepted_at_cutoff = running_accepted

    is_on_time = total_accepted_by_due >= target_qty
    is_completed = completion_date is not None

    completed_delay_days: Optional[float] = None
    if is_completed and completion_date is not None:
        delay = (completion_date - due_date).days
        completed_delay_days = max(0.0, float(delay))

    shortfall = max(0.0, 1.0 - (total_accepted_at_cutoff / max(1e-6, order_line.ordered_quantity)))

    return is_on_time, is_completed, completed_delay_days, shortfall


def calculate_operational_indicators(
    order_lines: List[OrderLineRecord],
    receipts: List[ReceiptRecord],
    cutoff_date: date,
    window_days: int = 30,
    required_fulfillment_fraction: float = 1.0,
    grace_days: int = 0,
    cold_start_threshold: int = 10,
) -> OperationalMetrics:
    """Calculates L, D, T, F operational metrics for a supplier as of cutoff_date.

    Windows:
      - Recent window: [cutoff_date - window_days, cutoff_date]
      - Previous window: [cutoff_date - 2*window_days, cutoff_date - window_days - 1]
    """
    recent_start = cutoff_date - timedelta(days=window_days)
    prev_start = cutoff_date - timedelta(days=2 * window_days)
    prev_end = recent_start - timedelta(days=1)

    # Filter lines due on or before cutoff_date
    due_lines = [l for l in order_lines if l.committed_due_date <= cutoff_date]
    total_due_count = len(due_lines)

    recent_lines = [
        l for l in due_lines
        if recent_start <= l.committed_due_date <= cutoff_date
    ]
    prev_lines = [
        l for l in due_lines
        if prev_start <= l.committed_due_date <= prev_end
    ]

    missing_factors: List[str] = []

    # 1. Recent Window Analysis
    recent_on_time_count = 0
    recent_completed_delays: List[float] = []
    recent_shortfalls: List[float] = []

    for l in recent_lines:
        is_on_time, is_completed, delay_days, shortfall = compute_order_line_delay(
            l, receipts, cutoff_date, required_fulfillment_fraction, grace_days
        )
        if is_on_time:
            recent_on_time_count += 1
        if is_completed and delay_days is not None:
            recent_completed_delays.append(delay_days)
        recent_shortfalls.append(shortfall)

    # L: Late fraction
    if len(recent_lines) > 0:
        on_time_rate = recent_on_time_count / len(recent_lines)
        L = 1.0 - on_time_rate
    else:
        on_time_rate = 1.0
        L = 0.0
        missing_factors.append("L")

    # D: Delay factor (scaled to 10 days)
    if len(recent_completed_delays) > 0:
        recent_mean_delay = float(np.mean(recent_completed_delays))
        D = clip(recent_mean_delay / 10.0, 0.0, 1.0)
    else:
        recent_mean_delay = 0.0
        D = 0.0
        missing_factors.append("D")

    # 2. Previous Window Analysis for Trend (T)
    prev_completed_delays: List[float] = []
    for l in prev_lines:
        _, is_completed, delay_days, _ = compute_order_line_delay(
            l, receipts, cutoff_date, required_fulfillment_fraction, grace_days
        )
        if is_completed and delay_days is not None:
            prev_completed_delays.append(delay_days)

    if len(prev_completed_delays) > 0 and len(recent_completed_delays) > 0:
        prev_mean_delay = float(np.mean(prev_completed_delays))
        # T scaled to 5 days
        T = clip((recent_mean_delay - prev_mean_delay) / 5.0, 0.0, 1.0)
    elif len(recent_completed_delays) > 0:
        # BUG-19 fix: recent data exists but no prior window — T can still be computed
        # as recent mean delay alone (no worsening trend detectable, T=0) but do NOT
        # mark T as missing since we have meaningful recent data.
        prev_mean_delay = 0.0
        T = 0.0
    else:
        # No recent data at all — T is genuinely missing
        prev_mean_delay = 0.0
        T = 0.0
        missing_factors.append("T")

    # F: Shortfall
    if len(recent_shortfalls) > 0:
        F = float(np.mean(recent_shortfalls))
    else:
        F = 0.0
        missing_factors.append("F")

    # Sufficiency determination
    if total_due_count == 0:
        sufficiency = SufficiencyState.NO_DATA
    elif total_due_count < cold_start_threshold:
        sufficiency = SufficiencyState.LIMITED_HISTORY
    else:
        sufficiency = SufficiencyState.ADEQUATE

    return OperationalMetrics(
        on_time_fulfillment_rate=round(on_time_rate, 4),
        late_fraction_L=round(L, 4),
        recent_mean_completed_delay_days=round(recent_mean_delay, 2),
        delay_factor_D=round(D, 4),
        previous_mean_completed_delay_days=round(prev_mean_delay, 2),
        deterioration_factor_T=round(T, 4),
        fulfillment_shortfall_F=round(F, 4),
        total_due_lines=total_due_count,
        recent_window_lines=len(recent_lines),
        previous_window_lines=len(prev_lines),
        sufficiency=sufficiency,
        missing_factors=missing_factors,
    )
