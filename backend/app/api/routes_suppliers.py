"""Supplier REST routes — reads from DB and computes live risk scores."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import List, Dict, Any, Optional

from backend.app.adapters.storage import get_sync_session
from backend.app.models.schema import (
    Supplier, SupplierMaterial, Material,
    PurchaseOrderLine, Receipt,
)
from backend.app.domain.metrics import calculate_operational_indicators
from backend.app.domain.scoring import calculate_risk_policy
from backend.app.domain.models_domain import (
    OrderLineRecord, ReceiptRecord, ExternalEvidenceStatus,
)

router = APIRouter(prefix="/api/suppliers", tags=["Suppliers"])


def _build_supplier_summary(
    supplier: Supplier,
    db: Session,
    cutoff: date,
) -> Dict[str, Any]:
    """Compute risk metrics for a supplier from DB records."""

    # --- Order lines ---
    db_lines = db.query(PurchaseOrderLine).filter(
        PurchaseOrderLine.supplier_id == supplier.id
    ).all()

    order_lines = [
        OrderLineRecord(
            id=l.id,
            supplier_id=l.supplier_id,
            material_id=l.material_id,
            po_number=l.po_number,
            line_number=l.line_number,
            ordered_quantity=l.ordered_quantity,
            unit=l.unit,
            committed_due_date=l.committed_due_date,
            created_at=l.created_at,
        )
        for l in db_lines
    ]

    # --- Receipts for those lines ---
    line_ids = [l.id for l in db_lines]
    db_receipts = db.query(Receipt).filter(
        Receipt.po_line_id.in_(line_ids)
    ).all() if line_ids else []

    receipts = [
        ReceiptRecord(
            id=r.id,
            po_line_id=r.po_line_id,
            accepted_quantity=r.accepted_quantity,
            rejected_quantity=r.rejected_quantity,
            received_at=r.received_at,
            recorded_at=r.recorded_at,
        )
        for r in db_receipts
    ]

    # --- Operational metrics ---
    metrics = calculate_operational_indicators(
        order_lines=order_lines,
        receipts=receipts,
        cutoff_date=cutoff,
    )

    # --- Risk score ---
    risk = calculate_risk_policy(
        L=metrics.late_fraction_L,
        D=metrics.delay_factor_D,
        T=metrics.deterioration_factor_T,
        F=metrics.fulfillment_shortfall_F,
        missing_factors=metrics.missing_factors,
        evidence_items=[],
        evidence_status=ExternalEvidenceStatus.NO_RELEVANT_EVIDENCE,
    )

    # --- Materials supplied ---
    links = db.query(SupplierMaterial).filter(
        SupplierMaterial.supplier_id == supplier.id
    ).all()
    mat_names = []
    for lnk in links:
        mat = db.query(Material).filter(Material.id == lnk.material_id).first()
        if mat:
            mat_names.append(mat.name)

    return {
        "id": supplier.id,
        "legal_name": supplier.legal_name,
        "aliases": supplier.aliases or [],
        "location": supplier.location or "",
        "materials_supplied": mat_names,
        "total_due_lines": metrics.total_due_lines,
        "on_time_rate": round(metrics.on_time_fulfillment_rate, 4),
        "late_fraction_L": round(metrics.late_fraction_L, 4),
        "delay_factor_D": round(metrics.delay_factor_D, 4),
        "trend_factor_T": round(metrics.deterioration_factor_T, 4),
        "shortfall_F": round(metrics.fulfillment_shortfall_F, 4),
        "internal_index_I": round(risk.internal_index_I, 2) if risk.internal_index_I is not None else None,
        "external_index_E": round(risk.external_index_E, 2) if risk.external_index_E is not None else None,
        "blended_risk_R": round(risk.blended_risk_R, 2) if risk.blended_risk_R is not None else 0.0,
        "band": risk.band.value,
        "external_status": ExternalEvidenceStatus.NO_RELEVANT_EVIDENCE.value,
        "critical_override": False,
        "override_reason": None,
        "last_assessed": datetime.utcnow().isoformat() + "Z",
    }


@router.get("")
def list_suppliers(db: Session = Depends(get_sync_session)):
    """Returns all suppliers from DB with live-calculated risk scores.
    Falls back to demo data if DB is empty."""
    suppliers = db.query(Supplier).all()

    if not suppliers:
        # Fall back to demo data if nothing imported yet
        from backend.app.api.routes_suppliers_demo import DEMO_SUPPLIERS
        return DEMO_SUPPLIERS

    cutoff = date.today()
    result = []
    for s in suppliers:
        try:
            summary = _build_supplier_summary(s, db, cutoff)
            result.append(summary)
        except Exception as e:
            # If scoring fails for one supplier, include minimal record
            result.append({
                "id": s.id, "legal_name": s.legal_name,
                "aliases": s.aliases or [], "location": s.location or "",
                "materials_supplied": [], "total_due_lines": 0,
                "on_time_rate": 1.0, "late_fraction_L": 0.0,
                "delay_factor_D": 0.0, "trend_factor_T": 0.0, "shortfall_F": 0.0,
                "internal_index_I": None, "external_index_E": None,
                "blended_risk_R": 0.0, "band": "low",
                "external_status": "unavailable", "critical_override": False,
                "override_reason": None, "last_assessed": datetime.utcnow().isoformat() + "Z",
            })

    # Sort highest risk first
    result.sort(key=lambda x: x["blended_risk_R"] or 0, reverse=True)
    return result


@router.get("/{supplier_id}")
def get_supplier(supplier_id: str, db: Session = Depends(get_sync_session)):
    """Returns detailed dossier for a specific supplier."""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return _build_supplier_summary(supplier, db, date.today())
