"""Alerts and Feedback REST routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

DEMO_ALERTS = [
    {
        "id": "alt-001",
        "supplier_id": "sup-001",
        "supplier_name": "Apex Polymers Ltd",
        "material_name": "Polyethylene Resin HD-500",
        "incident_key": "apex-polymers-facility-delay-2026-10",
        "severity": "critical",
        "status": "open",
        "created_at": "2026-10-09T14:32:00Z",
        "grounded_explanation": {
            "summary": "Supplier Apex Polymers' recent late fraction is 60%, and average completed delay rose from 2 to 6 days. One verified facility interruption contributes external evidence (E=72.0, R=61.15). Available resin covers 8 days at 100 kg/day. Under declared 12-day replenishment, a 4-day supply gap appears.",
            "drivers": [
                {"metric": "late_fraction_L", "label": "Late Fraction (L)", "value": "60.0%", "benchmark": "< 30%"},
                {"metric": "delay_trend_T", "label": "Completed Delay Rise", "value": "2.0d -> 6.0d", "benchmark": "Stable <= 2d"},
                {"metric": "blended_risk_R", "label": "Blended Risk Index (R)", "value": "61.15", "benchmark": "High Band >= 60"},
            ],
            "evidence_ids": ["ev-demo-001"],
            "evidence_excerpt": "Chemical industry update: regional supply disruption at feedstock crackers affecting resin pellet extrusion.",
            "evidence_source": "Petrochem Daily Bulletin (Verified Fixture)",
            "evidence_date": "2026-09-20",
            "impact_assumptions": {
                "material": "Polyethylene Resin HD-500",
                "available_stock": 800,
                "daily_burn": 100,
                "coverage_days": 8.0,
                "scenario_arrival_days": 12.0,
                "supply_gap_days": 4.0,
            },
            "suggested_actions": [
                "Confirm shipment status for open PO-2026-8802 immediately.",
                "Review approved backup supplier Delta Resins (normal lead time: 5 days).",
                "Reserve 200 kg buffer from secondary extrusion schedule if delay exceeds 4 days.",
            ],
            "limitations": "External news is synthetic demonstration data. Inventory model assumes constant 100 kg/day demand.",
        },
    },
    {
        "id": "alt-002",
        "supplier_id": "sup-003",
        "supplier_name": "FlexiFilm Global",
        "material_name": "High Barrier PVDC Film 25um",
        "incident_key": "flexifilm-trend-watch-2026-10",
        "severity": "watch",
        "status": "open",
        "created_at": "2026-10-09T14:32:00Z",
        "grounded_explanation": {
            "summary": "FlexiFilm shows gradual operational decline with 45% late fraction and delay increasing to 4 days. No external news detected (evidence-limited score R=40.25). Film stock covers 10 days with a 4-day stress gap.",
            "drivers": [
                {"metric": "late_fraction_L", "label": "Late Fraction (L)", "value": "45.0%", "benchmark": "< 30%"},
                {"metric": "single_source", "label": "Sole Source Vulnerability", "value": "Single Supplier", "benchmark": "No backup"},
            ],
            "evidence_ids": [],
            "impact_assumptions": {
                "material": "High Barrier PVDC Film 25um",
                "available_stock": 100,
                "daily_burn": 10,
                "coverage_days": 10.0,
                "scenario_arrival_days": 14.0,
                "supply_gap_days": 4.0,
            },
            "suggested_actions": [
                "Inquire with FlexiFilm production lead on upcoming slit rolls schedule.",
                "Begin pre-qualification testing for alternate barrier film suppliers.",
            ],
            "limitations": "Sole source dependency increases actual operational exposure beyond internal delivery index alone.",
        },
    },
]

FEEDBACK_STORE: List[Dict[str, Any]] = []


class AlertUpdatePayload(BaseModel):
    status: str
    reason: Optional[str] = None


class FeedbackPayload(BaseModel):
    reviewer_id: str = "purchasing_manager"
    disposition: str  # useful, false_alarm, unhelpful
    reason: Optional[str] = None


@router.get("")
def list_alerts():
    return DEMO_ALERTS


@router.get("/{alert_id}")
def get_alert(alert_id: str):
    for a in DEMO_ALERTS:
        if a["id"] == alert_id:
            return a
    raise HTTPException(status_code=404, detail="Alert not found")


@router.patch("/{alert_id}")
def update_alert(alert_id: str, payload: AlertUpdatePayload):
    for a in DEMO_ALERTS:
        if a["id"] == alert_id:
            a["status"] = payload.status
            a["acknowledged_at"] = datetime.utcnow().isoformat()
            a["acknowledged_by"] = "purchasing_lead"
            return a
    raise HTTPException(status_code=404, detail="Alert not found")


@router.post("/{alert_id}/feedback")
def submit_feedback(alert_id: str, payload: FeedbackPayload):
    item = {
        "alert_id": alert_id,
        "reviewer_id": payload.reviewer_id,
        "disposition": payload.disposition,
        "reason": payload.reason,
        "timestamp": datetime.utcnow().isoformat(),
    }
    FEEDBACK_STORE.append(item)
    return {"status": "recorded", "feedback": item}
