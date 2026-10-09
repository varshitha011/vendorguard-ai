"""Research Replay and Evaluation REST routes."""

from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter(prefix="/api/replay", tags=["Research Replay"])

REPLAY_BASELINES = [
    {
        "system": "B0",
        "name": "Simple Overdue Rule",
        "inputs": "Current overdue PO lines only",
        "alert_episode_precision": 0.38,
        "incident_recall": 0.52,
        "warning_lead_time_days": 0.8,
        "false_alert_burden": 1.45,
        "actionable_recall": 0.22,
        "top_k_agreement": 0.41,
    },
    {
        "system": "B1",
        "name": "Internal-Only Operational Policy",
        "inputs": "Historical delivery metrics (L, D, T, F)",
        "alert_episode_precision": 0.62,
        "incident_recall": 0.74,
        "warning_lead_time_days": 4.5,
        "false_alert_burden": 0.72,
        "actionable_recall": 0.58,
        "top_k_agreement": 0.68,
    },
    {
        "system": "B2",
        "name": "External-Only Evidence Policy",
        "inputs": "Verified public news signals alone",
        "alert_episode_precision": 0.44,
        "incident_recall": 0.48,
        "warning_lead_time_days": 7.2,
        "false_alert_burden": 0.89,
        "actionable_recall": 0.42,
        "top_k_agreement": 0.51,
    },
    {
        "system": "P1",
        "name": "Combined VendorGuard Policy",
        "inputs": "Internal history + Bounded external events (R)",
        "alert_episode_precision": 0.78,
        "incident_recall": 0.86,
        "warning_lead_time_days": 6.8,
        "false_alert_burden": 0.42,
        "actionable_recall": 0.75,
        "top_k_agreement": 0.79,
    },
    {
        "system": "P2",
        "name": "Impact-Aware Prioritization",
        "inputs": "P1 + Material Exposure Simulation (B[d])",
        "alert_episode_precision": 0.84,
        "incident_recall": 0.89,
        "warning_lead_time_days": 7.5,
        "false_alert_burden": 0.31,
        "actionable_recall": 0.84,
        "top_k_agreement": 0.92,
    },
]


@router.get("/baselines")
def get_baselines():
    return REPLAY_BASELINES
