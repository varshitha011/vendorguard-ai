"""Explainable scoring policy engine.

Implements Sections 10 & 12 of the VendorGuard AI Blueprint:
- Internal Index (I) with factor renormalization
- External Index (E) from auditable evidence contracts
- Blended Risk Index (R) with floor property max(I, 0.70*I + 0.30*E)
- Critical-event override logic
- Risk bands (Low < 30, Watch 30-59.99, High >= 60)
"""

from typing import List, Dict, Optional, Tuple
from .models_domain import (
    RiskBand,
    ExternalEvidenceStatus,
    RiskScoreResult,
    EvidenceItemRecord,
)

BASE_WEIGHTS = {
    "L": 0.40,
    "D": 0.25,
    "T": 0.20,
    "F": 0.15,
}

CRITICAL_EVENT_TYPES = {
    "facility_interruption",
    "insolvency_restructuring",
    "regulatory_shutdown",
    "force_majeure",
}


def calculate_internal_index(
    L: float,
    D: float,
    T: float,
    F: float,
    missing_factors: Optional[List[str]] = None,
) -> Tuple[Optional[float], Dict[str, float], bool]:
    """Calculates Internal Operational Risk Index I in [0, 100].

    Returns:
        (I_score, factor_contributions, is_partial)
    """
    if missing_factors is None:
        missing_factors = []

    available_keys = [k for k in BASE_WEIGHTS.keys() if k not in missing_factors]

    if not available_keys:
        return None, {}, True

    is_partial = len(missing_factors) > 0
    total_avail_weight = sum(BASE_WEIGHTS[k] for k in available_keys)

    # Renormalize weights
    norm_weights = {k: BASE_WEIGHTS[k] / total_avail_weight for k in available_keys}

    factor_vals = {"L": L, "D": D, "T": T, "F": F}
    contributions = {}
    weighted_sum = 0.0

    for k in available_keys:
        contrib = 100.0 * norm_weights[k] * factor_vals[k]
        contributions[k] = round(contrib, 2)
        weighted_sum += contrib

    I_score = round(weighted_sum, 2)
    return I_score, contributions, is_partial


def calculate_external_index(
    evidence_items: List[EvidenceItemRecord],
) -> Tuple[Optional[float], ExternalEvidenceStatus, Optional[EvidenceItemRecord]]:
    """Calculates External Evidence Index E in [0, 100] from supported public evidence items."""
    if not evidence_items:
        return None, ExternalEvidenceStatus.NO_RELEVANT_EVIDENCE, None

    # Filter to verified entity matches
    verified_items = [e for e in evidence_items if e.entity_match.lower() == "verified"]
    if not verified_items:
        # Check if there are ambiguous entities
        if any(e.entity_match.lower() == "ambiguous" for e in evidence_items):
            return None, ExternalEvidenceStatus.AMBIGUOUS_ENTITY, None
        return None, ExternalEvidenceStatus.NO_RELEVANT_EVIDENCE, None

    # Calculate event scores: e_j = severity * reliability * freshness
    scored_items: List[Tuple[float, EvidenceItemRecord]] = []
    for item in verified_items:
        score = item.severity * item.reliability_factor * item.freshness_factor
        scored_items.append((score, item))

    if not scored_items:
        return None, ExternalEvidenceStatus.NO_RELEVANT_EVIDENCE, None

    # E = 100 * max(e_j)
    scored_items.sort(key=lambda x: x[0], reverse=True)
    max_score, top_item = scored_items[0]
    E_score = round(100.0 * max_score, 2)

    return E_score, ExternalEvidenceStatus.RELIABLE_EVIDENCE, top_item


def calculate_risk_policy(
    L: float,
    D: float,
    T: float,
    F: float,
    evidence_items: Optional[List[EvidenceItemRecord]] = None,
    missing_factors: Optional[List[str]] = None,
    policy_version: str = "v1.0.0",
) -> RiskScoreResult:
    """Combines operational features and external evidence into a defensible risk score result."""
    if evidence_items is None:
        evidence_items = []

    I_score, factor_contribs, is_partial = calculate_internal_index(
        L, D, T, F, missing_factors=missing_factors
    )
    E_score, ext_status, top_evidence = calculate_external_index(evidence_items)

    blended_R: Optional[float] = None
    is_evidence_limited = False

    if I_score is not None and ext_status == ExternalEvidenceStatus.RELIABLE_EVIDENCE and E_score is not None:
        # R = max(I, 0.70*I + 0.30*E)
        blended = 0.70 * I_score + 0.30 * E_score
        blended_R = round(max(I_score, blended), 2)
    elif I_score is not None:
        # External evidence missing or unverified -> R = I with evidence-limited label
        blended_R = I_score
        is_evidence_limited = True
    else:
        # Only external evidence exists -> withhold combined score
        blended_R = None

    # Critical event override check
    critical_override_active = False
    override_reason = None
    if top_evidence and top_evidence.severity >= 0.75:
        if top_evidence.event_type.lower() in CRITICAL_EVENT_TYPES:
            critical_override_active = True
            override_reason = (
                f"Severe verified event detected ({top_evidence.event_type}, severity {top_evidence.severity:.2f}): "
                f"{top_evidence.supporting_excerpt}"
            )

    # Risk Band Determination
    score_for_band = blended_R if blended_R is not None else (I_score if I_score is not None else E_score)
    if score_for_band is None:
        band = RiskBand.LOW
    elif score_for_band >= 60.0 or critical_override_active:
        band = RiskBand.HIGH
    elif score_for_band >= 30.0:
        band = RiskBand.WATCH
    else:
        band = RiskBand.LOW

    return RiskScoreResult(
        internal_index_I=I_score,
        external_index_E=E_score,
        blended_risk_R=blended_R,
        band=band,
        factor_contributions=factor_contribs,
        is_partial=is_partial,
        is_evidence_limited=is_evidence_limited,
        critical_override_active=critical_override_active,
        override_reason=override_reason,
        policy_version=policy_version,
    )
