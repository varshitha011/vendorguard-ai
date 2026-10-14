"""CSV Import REST routes."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.app.adapters.storage import get_sync_session
from backend.app.services.import_service import validate_and_stage_csv, commit_staged_import

router = APIRouter(prefix="/api/imports", tags=["Imports"])


class ImportPreviewRequest(BaseModel):
    file_type: str
    csv_text: str
    tenant_id: str = "tenant-demo"


@router.post("/preview", status_code=200)
def preview_import(payload: ImportPreviewRequest):
    """Validates raw CSV text and stages for review without business writes."""
    try:
        res = validate_and_stage_csv(
            file_type=payload.file_type,
            csv_text=payload.csv_text,
            tenant_id=payload.tenant_id,
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{preview_id}/commit", status_code=201)
def commit_import(preview_id: str, db: Session = Depends(get_sync_session)):
    """Commits a validated staged import transactionally."""
    try:
        res = commit_staged_import(preview_id=preview_id, db=db)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
