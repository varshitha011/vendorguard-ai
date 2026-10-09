"""Materials and Inventory Exposure REST routes."""

from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter(prefix="/api/materials", tags=["Materials"])

DEMO_MATERIALS = [
    {
        "material_id": "mat-001",
        "material_name": "Polyethylene Resin HD-500",
        "criticality": "tier_1",
        "unit": "kg",
        "on_hand_stock": 800,
        "reserved_stock": 0,
        "available_stock": 800,
        "daily_consumption": 100,
        "coverage_days": 8.0,
        "scenario_arrival_days": 12.0,
        "scenario_gap_days": 4.0,
        "day_to_stockout": 9,
        "primary_supplier": "Apex Polymers Ltd",
        "has_alternate_supplier": True,
        "alternate_suppliers": [
            {"name": "Delta Resins & Chemicals", "lead_time_days": 5, "approved": True},
            {"name": "NovaPlast Resins Corp", "lead_time_days": 7, "approved": True},
        ],
        "trajectory_base": [
            {"day": i + 1, "date_str": f"2026-10-{i+10:02d}", "balance": 800 + (1000 if i >= 7 else 0) - (i + 1) * 100, "is_stockout": False}
            for i in range(30)
        ],
        "trajectory_stress": [
            {"day": i + 1, "date_str": f"2026-10-{i+10:02d}", "balance": 800 + (1000 if i >= 13 else 0) - (i + 1) * 100, "is_stockout": (800 + (1000 if i >= 13 else 0) - (i + 1) * 100) < 0}
            for i in range(30)
        ],
    },
    {
        "material_id": "mat-002",
        "material_name": "High Barrier PVDC Film 25um",
        "criticality": "tier_1",
        "unit": "rolls",
        "on_hand_stock": 120,
        "reserved_stock": 20,
        "available_stock": 100,
        "daily_consumption": 10,
        "coverage_days": 10.0,
        "scenario_arrival_days": 14.0,
        "scenario_gap_days": 4.0,
        "day_to_stockout": 11,
        "primary_supplier": "FlexiFilm Global",
        "has_alternate_supplier": False,
        "alternate_suppliers": [],
        "trajectory_base": [
            {"day": i + 1, "date_str": f"2026-10-{i+10:02d}", "balance": max(0, 100 - (i + 1) * 10 + (150 if i >= 9 else 0)), "is_stockout": False}
            for i in range(30)
        ],
        "trajectory_stress": [
            {"day": i + 1, "date_str": f"2026-10-{i+10:02d}", "balance": 100 - (i + 1) * 10 + (150 if i >= 15 else 0), "is_stockout": (100 - (i + 1) * 10 + (150 if i >= 15 else 0)) < 0}
            for i in range(30)
        ],
    },
    {
        "material_id": "mat-003",
        "material_name": "White Masterbatch MB-01",
        "criticality": "tier_2",
        "unit": "kg",
        "on_hand_stock": 450,
        "reserved_stock": 50,
        "available_stock": 400,
        "daily_consumption": 25,
        "coverage_days": 16.0,
        "scenario_arrival_days": 12.0,
        "scenario_gap_days": 0.0,
        "day_to_stockout": None,
        "primary_supplier": "ChromaColor Labs",
        "has_alternate_supplier": True,
        "alternate_suppliers": [{"name": "Spectrum Pigments", "lead_time_days": 4, "approved": True}],
        "trajectory_base": [
            {"day": i + 1, "date_str": f"2026-10-{i+10:02d}", "balance": 400 - (i + 1) * 25 + (300 if i >= 9 else 0), "is_stockout": False}
            for i in range(30)
        ],
        "trajectory_stress": [
            {"day": i + 1, "date_str": f"2026-10-{i+10:02d}", "balance": 400 - (i + 1) * 25 + (300 if i >= 15 else 0), "is_stockout": False}
            for i in range(30)
        ],
    },
]


@router.get("")
def list_materials():
    return DEMO_MATERIALS
