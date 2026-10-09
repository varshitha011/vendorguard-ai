"""Supplier REST routes."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from backend.app.adapters.storage import get_sync_session
from backend.app.models.schema import Supplier, Assessment

router = APIRouter(prefix="/api/suppliers", tags=["Suppliers"])

# Default Mode A response data for instant responsiveness
from backend.app.domain.scoring import calculate_risk_policy
from backend.app.domain.models_domain import EvidenceItemRecord
from datetime import datetime

DEMO_SUPPLIERS = [
    {
        "id": "sup-001",
        "legal_name": "Apex Polymers Ltd",
        "aliases": ["Apex Poly", "Apex Chem"],
        "location": "Houston, TX",
        "materials_supplied": ["Polyethylene Resin HD-500"],
        "total_due_lines": 48,
        "on_time_rate": 0.40,
        "late_fraction_L": 0.60,
        "delay_factor_D": 0.60,
        "trend_factor_T": 0.80,
        "shortfall_F": 0.10,
        "internal_index_I": 56.5,
        "external_index_E": 72.0,
        "blended_risk_R": 61.15,
        "band": "high",
        "external_status": "reliable_evidence",
        "critical_override": True,
        "override_reason": "Verified facility disruption reported on petrochemical feed lines.",
        "last_assessed": "2026-10-09T14:30:00Z",
    },
    {
        "id": "sup-002",
        "legal_name": "NovaPlast Resins Corp",
        "aliases": ["NovaPlast", "Nova Polymers"],
        "location": "Baton Rouge, LA",
        "materials_supplied": ["Polyethylene Resin LD-200"],
        "total_due_lines": 36,
        "on_time_rate": 0.88,
        "late_fraction_L": 0.12,
        "delay_factor_D": 0.10,
        "trend_factor_T": 0.05,
        "shortfall_F": 0.02,
        "internal_index_I": 11.2,
        "external_index_E": None,
        "blended_risk_R": 11.2,
        "band": "low",
        "external_status": "no_relevant_evidence",
        "critical_override": False,
        "last_assessed": "2026-10-09T14:30:00Z",
    },
    {
        "id": "sup-003",
        "legal_name": "FlexiFilm Global",
        "aliases": ["FlexiFilm", "Flexi Extrusions"],
        "location": "Greenville, SC",
        "materials_supplied": ["High Barrier PVDC Film 25um"],
        "total_due_lines": 24,
        "on_time_rate": 0.55,
        "late_fraction_L": 0.45,
        "delay_factor_D": 0.40,
        "trend_factor_T": 0.50,
        "shortfall_F": 0.15,
        "internal_index_I": 40.25,
        "external_index_E": None,
        "blended_risk_R": 40.25,
        "band": "watch",
        "external_status": "no_relevant_evidence",
        "critical_override": False,
        "last_assessed": "2026-10-09T14:30:00Z",
    },
    {
        "id": "sup-004",
        "legal_name": "PackPro Corrugated Co",
        "aliases": ["PackPro Boxes"],
        "location": "Columbus, OH",
        "materials_supplied": ["3-Ply Corrugated Shipping Cartons"],
        "total_due_lines": 52,
        "on_time_rate": 0.94,
        "late_fraction_L": 0.06,
        "delay_factor_D": 0.05,
        "trend_factor_T": 0.0,
        "shortfall_F": 0.01,
        "internal_index_I": 5.8,
        "external_index_E": None,
        "blended_risk_R": 5.8,
        "band": "low",
        "external_status": "no_relevant_evidence",
        "critical_override": False,
        "last_assessed": "2026-10-09T14:30:00Z",
    },
    {
        "id": "sup-005",
        "legal_name": "ChromaColor Labs",
        "aliases": ["ChromaColor"],
        "location": "McHenry, IL",
        "materials_supplied": ["White Masterbatch MB-01"],
        "total_due_lines": 18,
        "on_time_rate": 0.65,
        "late_fraction_L": 0.35,
        "delay_factor_D": 0.30,
        "trend_factor_T": 0.40,
        "shortfall_F": 0.08,
        "internal_index_I": 30.7,
        "external_index_E": 45.0,
        "blended_risk_R": 35.0,
        "band": "watch",
        "external_status": "reliable_evidence",
        "critical_override": False,
        "last_assessed": "2026-10-09T14:30:00Z",
    },
    {
        "id": "sup-006",
        "legal_name": "ShieldBarrier Films",
        "aliases": ["ShieldBarrier"],
        "location": "Allentown, PA",
        "materials_supplied": ["Biaxially-Oriented PP Film"],
        "total_due_lines": 30,
        "on_time_rate": 0.90,
        "late_fraction_L": 0.10,
        "delay_factor_D": 0.10,
        "trend_factor_T": 0.0,
        "shortfall_F": 0.02,
        "internal_index_I": 9.8,
        "external_index_E": None,
        "blended_risk_R": 9.8,
        "band": "low",
        "external_status": "no_relevant_evidence",
        "critical_override": False,
        "last_assessed": "2026-10-09T14:30:00Z",
    },
    {
        "id": "sup-007",
        "legal_name": "Delta Resins & Chemicals",
        "aliases": ["Delta Resins"],
        "location": "Beaumont, TX",
        "materials_supplied": ["Polyethylene Resin HD-500 (Backup)"],
        "total_due_lines": 12,
        "on_time_rate": 0.83,
        "late_fraction_L": 0.17,
        "delay_factor_D": 0.20,
        "trend_factor_T": 0.10,
        "shortfall_F": 0.05,
        "internal_index_I": 14.5,
        "external_index_E": None,
        "blended_risk_R": 14.5,
        "band": "low",
        "external_status": "no_relevant_evidence",
        "critical_override": False,
        "last_assessed": "2026-10-09T14:30:00Z",
    },
]


@router.get("")
def list_suppliers():
    """Returns suppliers with latest calculated risk indicators."""
    return DEMO_SUPPLIERS


@router.get("/{supplier_id}")
def get_supplier(supplier_id: str):
    """Returns detailed dossier for a specific supplier."""
    for s in DEMO_SUPPLIERS:
        if s["id"] == supplier_id:
            return s
    raise HTTPException(status_code=404, detail="Supplier not found")
