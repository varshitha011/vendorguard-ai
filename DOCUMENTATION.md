# VendorGuard AI
## Project Documentation

---

## 1. Project Overview

**VendorGuard AI** is an Explainable Supplier Monitoring and Production-Disruption Decision Support system designed for small manufacturers. It helps purchasing managers and production planners track supplier reliability, simulate production exposure, and receive grounded, citation-backed decision support before stockouts occur.

**GitHub Repository:** https://github.com/varshitha011/vendorguard-ai

---

## 2. Problem Statement

Small manufacturers face significant risk when suppliers fail to deliver materials on time or in full. Traditional monitoring relies on manual tracking and gut feeling. VendorGuard AI automates supplier risk scoring using real delivery data, inventory simulation, and external evidence — giving purchasing teams actionable, explainable alerts before production is disrupted.

---

## 3. Key Features

| Feature | Description |
|---------|-------------|
| **Operational Risk Index (I)** | Calculated from delivery delay trends, late fractions, and shortfall records |
| **External Evidence Auditing (E)** | Tracks public events (strikes, disasters) with auditable citations |
| **Blended Risk Score (R)** | Combines internal and external scores: R = max(I, 0.70×I + 0.30×E) |
| **Risk Bands** | Low (< 30), Watch (30–60), High (≥ 60) |
| **Inventory Burn-Down Simulation** | Calculates how many days of stock remain given daily usage |
| **Historical Replay Studio** | Compare detection rules across different alert thresholds |
| **CSV Data Import** | Import suppliers, materials, PO lines, receipts, inventory and demand data |
| **Action Queue** | Prioritized list of suppliers requiring immediate attention |

---

## 4. Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS | Web UI |
| **Backend** | FastAPI, Python | REST API |
| **Database** | SQLite + SQLAlchemy ORM | Data persistence |
| **AI Domain** | Custom Python scoring engine | Risk calculations |
| **Icons** | Lucide Icons | UI icons |
| **Async DB** | aiosqlite | Async database access |
| **Validation** | Pydantic | Request/response validation |
| **Testing** | pytest | Unit tests |

---

## 5. Architecture

```
Browser (Next.js UI)
        │
        │  HTTP REST API
        ▼
FastAPI Backend (Python)
        │
        ├── routes_suppliers.py   → Supplier list + risk scores
        ├── routes_materials.py   → Material coverage + inventory
        ├── routes_alerts.py      → Action queue + feedback
        ├── routes_monitoring.py  → AI assessment runs
        ├── routes_imports.py     → CSV data import
        └── routes_replay.py      → Historical replay studio
        │
        ├── domain/metrics.py     → Compute L, D, T, F factors
        ├── domain/scoring.py     → Compute I, E, R, band
        ├── domain/impact.py      → Inventory burn-down simulation
        │
        └── SQLite Database
                │
                ├── suppliers
                ├── materials
                ├── supplier_materials
                ├── purchase_order_lines
                ├── receipts
                ├── inventory_snapshots
                ├── demand_forecasts
                ├── monitoring_runs
                ├── assessments
                ├── evidence_items
                ├── alerts
                └── alert_feedback
```

---

## 6. Database Schema

### Core Tables

| Table | Key Fields | Purpose |
|-------|-----------|---------|
| `tenants` | id, name | Multi-tenant workspace |
| `suppliers` | id, tenant_id, legal_name, aliases, location | Supplier registry |
| `materials` | id, tenant_id, name, canonical_unit, criticality | Material catalogue |
| `supplier_materials` | supplier_id, material_id, lead_time_days | Supplier-material links |
| `purchase_order_lines` | po_number, supplier_id, material_id, ordered_qty, due_date | Orders placed |
| `receipts` | po_line_id, accepted_qty, rejected_qty, received_at | Deliveries received |
| `inventory_snapshots` | material_id, on_hand_quantity, observed_at | Stock levels |
| `demand_forecasts` | material_id, date, daily_quantity | Consumption projections |
| `monitoring_runs` | id, tenant_id, status, summary_counts | AI assessment jobs |
| `assessments` | id, supplier_id, run_id, index_score, band | Risk scores |
| `evidence_items` | id, supplier_id, event_type, severity | External news/events |
| `alerts` | id, assessment_id, severity, status | Generated alerts |
| `alert_feedback` | id, alert_id, disposition, reason | User feedback |

---

## 7. Risk Scoring Formula

### Step 1 — Operational Metrics

| Factor | Formula | Meaning |
|--------|---------|---------|
| **L** (Late fraction) | Late orders ÷ Total orders | How often supplier is late |
| **D** (Delay factor) | Mean delay ÷ 10 days | How late on average |
| **T** (Trend factor) | (Recent mean − Prior mean) ÷ 5 | Getting worse? |
| **F** (Shortfall) | 1 − (Accepted qty ÷ Ordered qty) | Under-delivering? |

### Step 2 — Internal Index

```
I = 100 × (0.40×L + 0.25×D + 0.20×T + 0.15×F)
```

### Step 3 — Blended Risk Score

```
R = max(I, 0.70×I + 0.30×E)
```

### Step 4 — Risk Band

| Band | Score |
|------|-------|
| Low | R < 30 |
| Watch | 30 ≤ R < 60 |
| High | R ≥ 60 |

---

## 8. CSV Import System

Import files in this exact order:

| Order | Type | Key Fields |
|-------|------|-----------|
| 1 | suppliers | legal_name, aliases, domain, location |
| 2 | materials | name, canonical_unit, criticality |
| 3 | supplier_materials | supplier_name, material_name, normal_lead_time_days |
| 4 | purchase_order_lines | po_number, supplier_name, ordered_quantity, committed_due_date |
| 5 | receipts | po_number, accepted_quantity, rejected_quantity, received_at |
| 6 | inventory_snapshots | material_name, on_hand_quantity, observed_at |
| 7 | demand_forecasts | material_name, date, daily_quantity |

---

## 9. API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/suppliers` | All suppliers with live risk scores |
| GET | `/api/suppliers/{id}` | Single supplier detail |
| GET | `/api/materials` | Material coverage |
| GET | `/api/alerts` | Active alerts |
| PATCH | `/api/alerts/{id}` | Update alert status |
| POST | `/api/monitoring-runs` | Trigger AI assessment |
| GET | `/api/monitoring-runs/{id}` | Check run status |
| POST | `/api/imports/preview` | Validate CSV |
| POST | `/api/imports/{id}/commit` | Commit import |
| GET | `/health` | Health check |

---

## 10. Frontend Pages

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/` | Overview with risk summary |
| Supplier Network | `/suppliers` | All suppliers by risk |
| Material Coverage | `/materials` | Stock and coverage days |
| Action Queue | `/alerts` | Alerts needing attention |
| Monitoring Runs | `/runs` | Assessment history |
| Data Imports | `/imports` | CSV upload |
| Replay Studio | `/replay` | Baseline comparisons |

---

## 11. How to Run Locally

```powershell
# Clone
git clone https://github.com/varshitha011/vendorguard-ai.git
cd vendorguard-ai

# Python setup
python -m venv .venv
.\.venv\Scripts\activate
pip install -r backend/requirements.txt

# Frontend setup
cd apps/web
npm install
cd ../..

# Run everything
npm run dev
```

- Frontend: http://localhost:3000
- API Docs: http://127.0.0.1:8000/docs

---

## 12. Bug Fixes Applied (22 total)

| Severity | Count | Examples |
|----------|-------|---------|
| High | 4 | Missing db.rollback(), wrong severity type, silent error swallowing |
| Medium | 13 | Missing ORM cascades, invalid aiosqlite arg, status contract mismatch |
| Low | 5 | Unused requirements, wrong HTTP status codes |

---

## 13. Synthetic Test Data (sample-data/)

| File | Records |
|------|---------|
| suppliers.csv | 100 |
| materials.csv | 20 |
| supplier_materials.csv | 45 |
| purchase_order_lines.csv | 171 |
| receipts.csv | 159 |
| inventory_snapshots.csv | 17 |
| demand_forecasts.csv | 510 |

> ⚠️ All data is synthetic — not real supplier information.

---

## 14. Git Commit History

| Commit | Description |
|--------|-------------|
| `5b1a242` | Suppliers page reads from real DB with live risk scores |
| `1f4b4af` | Fixed CSV comment lines breaking import |
| `afc9d94` | Added 100-supplier synthetic test dataset |
| `919c02c` | Fixed 22 bugs across backend and frontend |
| `0c0358a` | Initial VendorGuard AI codebase |
