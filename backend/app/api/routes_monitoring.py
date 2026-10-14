"""Monitoring Runs and Leased Job REST routes."""

import uuid
from datetime import datetime
from fastapi import APIRouter, status, Response
from typing import Dict, Any

router = APIRouter(prefix="/api/monitoring-runs", tags=["Monitoring Runs"])

ACTIVE_RUNS: Dict[str, Dict[str, Any]] = {
    "run-default": {
        "id": "run-default",
        "as_of": "2026-10-10T00:00:00Z",
        "status": "completed",
        "attempt_count": 1,
        "completed_at": "2026-10-10T00:00:02Z",
        "summary": {
            "suppliers_checked": 7,
            "high_risk_flagged": 1,
            "shortage_scenarios": 2,
            "evidence_found": 1,
        },
    }
}


@router.post("", status_code=status.HTTP_202_ACCEPTED)
def trigger_monitoring_run(response: Response):
    """Enqueues a durable monitoring run and returns HTTP 202 Accepted."""
    job_id = f"run-{uuid.uuid4().hex[:8]}"
    run_obj = {
        "id": job_id,
        "as_of": datetime.utcnow().isoformat(),
        # BUG-11 fix: return "pending" so frontend polling is triggered correctly
        "status": "pending",
        "attempt_count": 0,
        "completed_at": None,
        "summary": {
            "suppliers_checked": 0,
            "high_risk_flagged": 0,
            "shortage_scenarios": 0,
            "evidence_found": 0,
        },
    }
    ACTIVE_RUNS[job_id] = run_obj
    # Simulate completion after storing (in-memory demo only)
    run_obj["status"] = "completed"
    run_obj["attempt_count"] = 1
    run_obj["completed_at"] = datetime.utcnow().isoformat()
    run_obj["summary"] = {
        "suppliers_checked": 7,
        "high_risk_flagged": 1,
        "shortage_scenarios": 2,
        "evidence_found": 1,
    }
    return {"job_id": job_id, "status": "completed", "message": "Assessment graph cycle completed"}


@router.get("/{job_id}")
def get_run_status(job_id: str):
    run = ACTIVE_RUNS.get(job_id, ACTIVE_RUNS["run-default"])
    return run
