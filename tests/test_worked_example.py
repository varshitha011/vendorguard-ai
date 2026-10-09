"""Unit tests verifying the exact Section 12 worked example and domain math contracts."""

import pytest
from datetime import date, datetime, timedelta

from backend.app.domain.models_domain import (
    MaterialCriticality,
    RiskBand,
    ExternalEvidenceStatus,
    EvidenceItemRecord,
)
from backend.app.domain.metrics import clip
from backend.app.domain.scoring import (
    calculate_internal_index,
    calculate_external_index,
    calculate_risk_policy,
)
from backend.app.domain.impact import (
    calculate_coverage,
    calculate_scenario_gap,
    simulate_inventory_trajectory,
    rank_priority_key,
    evaluate_material_exposure,
)


def test_section_12_worked_example_exact_match():
    """Verifies Section 12 declared arithmetic with exact precision:

    L = 0.60
    recent mean delay = 6 days, previous mean delay = 2 days -> D = 0.60, T = 0.80
    F = 0.10
    I = 56.50
    E = 72.00
    R = 61.15
    coverage = 8 days, scenario arrival = 12 days -> scenario gap = 4 days
    """
    # 1. Inputs
    L = 0.60
    recent_mean_delay = 6.0
    prev_mean_delay = 2.0
    F = 0.10

    # 2. Intermediate factors
    D = clip(recent_mean_delay / 10.0, 0.0, 1.0)
    T = clip((recent_mean_delay - prev_mean_delay) / 5.0, 0.0, 1.0)
    assert D == pytest.approx(0.60, abs=1e-4)
    assert T == pytest.approx(0.80, abs=1e-4)

    # 3. Internal index I
    I_score, contribs, is_partial = calculate_internal_index(L, D, T, F)
    assert not is_partial
    assert I_score == pytest.approx(56.50, abs=1e-2)
    assert contribs["L"] == pytest.approx(24.0, abs=1e-2)
    assert contribs["D"] == pytest.approx(15.0, abs=1e-2)
    assert contribs["T"] == pytest.approx(16.0, abs=1e-2)
    assert contribs["F"] == pytest.approx(1.5, abs=1e-2)

    # 4. External evidence E
    fixture = EvidenceItemRecord(
        evidence_id="ev-demo-001",
        supplier_id="supplier-demo-a",
        source_url="https://example.org/illustrative-not-a-real-report",
        published_at=datetime(2026, 9, 20, 8, 0),
        fetched_at=datetime(2026, 9, 21, 8, 0),
        event_type="facility_interruption",
        entity_match="verified",
        source_quality="primary_or_verified_report",
        severity=0.80,
        reliability_factor=0.90,
        freshness_factor=1.00,
        supporting_excerpt="ILLUSTRATIVE FIXTURE: facility operations are temporarily interrupted.",
        is_synthetic=True,
    )
    E_score, ext_status, top_evidence = calculate_external_index([fixture])
    assert ext_status == ExternalEvidenceStatus.RELIABLE_EVIDENCE
    assert E_score == pytest.approx(72.00, abs=1e-2)

    # 5. Combined risk policy R
    policy_res = calculate_risk_policy(L, D, T, F, evidence_items=[fixture])
    assert policy_res.internal_index_I == pytest.approx(56.50, abs=1e-2)
    assert policy_res.external_index_E == pytest.approx(72.00, abs=1e-2)
    assert policy_res.blended_risk_R == pytest.approx(61.15, abs=1e-2)
    assert policy_res.band == RiskBand.HIGH
    assert policy_res.critical_override_active is True  # severity 0.80 >= 0.75 facility_interruption

    # 6. Production-Impact coverage & scenario gap
    on_hand_resin = 800.0
    reserved_resin = 0.0
    expected_daily_consumption = 100.0
    available_stock, coverage_days = calculate_coverage(
        on_hand_resin, reserved_resin, expected_daily_consumption
    )
    assert available_stock == pytest.approx(800.0, abs=1e-2)
    assert coverage_days == pytest.approx(8.0, abs=1e-2)

    scenario_arrival_days = 12.0
    gap = calculate_scenario_gap(coverage_days, scenario_arrival_days)
    assert gap == pytest.approx(4.0, abs=1e-2)


def test_internal_index_renormalization_on_missing_factors():
    """If delay or trend factor is missing (e.g. no completed lines), renormalize weights."""
    L = 0.50
    D = 0.0
    T = 0.0
    F = 0.20
    # Missing D and T
    I_score, contribs, is_partial = calculate_internal_index(
        L, D, T, F, missing_factors=["D", "T"]
    )
    assert is_partial
    # Total available weight: 0.40 (L) + 0.15 (F) = 0.55
    # norm_w_L = 0.40 / 0.55 = 0.72727
    # norm_w_F = 0.15 / 0.55 = 0.27273
    # I = 100 * (0.72727*0.5 + 0.27273*0.2) = 100 * (0.36364 + 0.05455) = 41.82
    expected_I = 100.0 * ((0.40 / 0.55) * 0.50 + (0.15 / 0.55) * 0.20)
    assert I_score == pytest.approx(round(expected_I, 2), abs=0.05)


def test_floor_property_prevents_external_event_from_reducing_high_operational_risk():
    """An operational risk I of 80 should not be reduced by a mild external event E of 30."""
    L = 0.90
    D = 0.80
    T = 0.80
    F = 0.60
    # Create mild external event: severity 0.3, rel 1.0, fresh 1.0 -> E = 30
    mild_fixture = EvidenceItemRecord(
        evidence_id="ev-mild",
        supplier_id="supplier-b",
        source_url="https://example.org",
        published_at=datetime(2026, 9, 20),
        fetched_at=datetime(2026, 9, 21),
        event_type="general_notice",
        entity_match="verified",
        source_quality="secondary",
        severity=0.30,
        reliability_factor=1.00,
        freshness_factor=1.00,
        supporting_excerpt="Minor update.",
        is_synthetic=True,
    )
    I_score, _, _ = calculate_internal_index(L, D, T, F)
    # I_score will be > 75
    res = calculate_risk_policy(L, D, T, F, [mild_fixture])
    # 0.70*I + 0.30*30 would be lower than I, but max(I, blended) keeps it at I!
    assert res.blended_risk_R == I_score


def test_inventory_daily_trajectory_simulation():
    """Verifies daily balance B[d] = B[d-1] + receipts - demand and stockout detection."""
    start_d = date(2026, 10, 1)
    init_stock = 300.0
    daily_burn = 100.0
    # Day 1: 300 - 100 = 200
    # Day 2: 200 - 100 = 100
    # Day 3: 100 - 100 = 0
    # Day 4: 0 - 100 = -100 (stockout on day 4!)
    # Day 5: scheduled receipt of 250 arrives -> -100 + 250 - 100 = 50
    receipts = {
        start_d + timedelta(days=5): 250.0
    }
    traj, stockout_day = simulate_inventory_trajectory(
        start_date=start_d,
        initial_available_stock=init_stock,
        daily_consumption=daily_burn,
        scheduled_receipts_by_date=receipts,
        horizon_days=6,
    )
    assert stockout_day == 4
    assert traj[0].ending_balance == 200.0
    assert traj[1].ending_balance == 100.0
    assert traj[2].ending_balance == 0.0
    assert traj[3].ending_balance == -100.0
    assert traj[3].is_stockout is True
    assert traj[4].ending_balance == 50.0
    assert traj[4].is_stockout is False


def test_lexicographical_prioritization():
    """Shortage urgency takes precedence over supplier risk score alone."""
    start_d = date(2026, 10, 1)
    # Material 1: stockout in 2 days, moderate supplier risk 50
    exp_urgent = evaluate_material_exposure(
        material_id="mat-1",
        material_name="Resin A",
        criticality=MaterialCriticality.TIER_1,
        unit="kg",
        on_hand_stock=200.0,
        reserved_stock=0.0,
        daily_consumption=100.0,
        start_date=start_d,
        normal_receipts_by_date={},
        normal_lead_time_days=10.0,
        stress_delay_days=5.0,
    )
    # Material 2: no stockout (surplus), but high supplier risk 90
    exp_safe = evaluate_material_exposure(
        material_id="mat-2",
        material_name="Cartons B",
        criticality=MaterialCriticality.TIER_1,
        unit="units",
        on_hand_stock=5000.0,
        reserved_stock=0.0,
        daily_consumption=50.0,
        start_date=start_d,
        normal_receipts_by_date={},
        normal_lead_time_days=10.0,
        stress_delay_days=5.0,
    )

    key_urgent = rank_priority_key(exp_urgent, supplier_risk_score=50.0)
    key_safe = rank_priority_key(exp_safe, supplier_risk_score=90.0)

    # Key urgent has day_to_stockout = 3, key safe has day_to_stockout = 999
    assert key_urgent < key_safe  # lower key = higher priority triage rank
