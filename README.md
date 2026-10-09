# VendorGuard AI

> **Explainable Supplier Monitoring & Production-Disruption Decision Support for Small Manufacturers**

VendorGuard AI helps purchasing managers and production planners track supplier reliability, simulate production exposure, and receive grounded, citation-backed decision support before stockouts occur.

---

## Architecture Overview

- **Frontend (`apps/web`)**: Next.js 14 App Router, TypeScript, Tailwind CSS, Lucide Icons.
- **Backend (`backend`)**: FastAPI, SQLite persistence, LangGraph monitoring pipelines.
- **Root Orchestration**: Single-command development runner (`npm run dev`) that coordinates both services.

---

## Getting Started

### Prerequisites

- Node.js (v18+)
- Python (3.11+)

### Installation

1. **Install Python dependencies:**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate  # On Windows
   # or source .venv/bin/activate on Unix
   pip install -r backend/requirements.txt
   ```

2. **Install frontend dependencies:**
   ```bash
   cd apps/web
   npm install
   cd ../..
   ```

### Running Locally

To start both the FastAPI backend (`http://127.0.0.1:8000`) and the Next.js frontend (`http://localhost:3000`) concurrently:

```bash
npm run dev
```

Or run individual services:
- **Frontend only:** `npm run dev:web`
- **Backend only:** `npm run dev:backend`

---

## Key Features

1. **Deterministic Operational Risk Index ($I$)**: Metric calculated from real delivery delay trends, late fractions, and shortfall records.
2. **External Evidence Auditing ($E$)**: Bounded, sanitized public event tracking with auditable citations.
3. **Daily Inventory Burn-Down Simulation**: Forward-looking material stockout simulation with supply gap analysis.
4. **Historical Replay Studio**: Comparative baseline evaluations across detection rules and lead times.
