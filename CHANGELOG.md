# VendorGuard AI — Changelog

## [Unreleased] — feature/vendorguard-improvements

### Bug Fixes
- Fixed invalid `check_same_thread` argument on aiosqlite engine (BUG-04)
- Added missing ORM back-references on Tenant for Assessment, InventorySnapshot, DemandForecast, Alert (BUG-05, 06, 07, 17)
- Added `db.rollback()` on exception in `commit_staged_import` to prevent partial writes (BUG-09)
- Fixed alert severity union — removed `"watch"` which is a risk band, not a severity level (BUG-13/25)
- Fixed silent error swallowing in `getSuppliers`, `getMaterials`, `getAlerts` (BUG-23)
- Fixed `node_traces` typed as required but never returned by backend (BUG-27)
- Fixed T deterioration factor incorrectly marked missing when recent data exists (BUG-19)
- Removed unused `pandas`, `langgraph`, `langchain-core` from requirements (BUG-01, 02)
- Fixed monitoring run status contract mismatch (BUG-11)
- Added error logging in DataProvider refresh (BUG-26)

### New Features
- `routes_suppliers.py` now reads from the real database and computes live risk scores from PO/receipt data
- Added `routes_suppliers_demo.py` as fallback when DB is empty
- Added 100-supplier synthetic test dataset across all 7 CSV import types:
  - `suppliers.csv` — 100 suppliers
  - `materials.csv` — 20 materials
  - `supplier_materials.csv` — 45 supplier-material links
  - `purchase_order_lines.csv` — 171 PO lines
  - `receipts.csv` — 159 delivery receipts
  - `inventory_snapshots.csv` — 17 stock snapshots
  - `demand_forecasts.csv` — 510 daily forecasts

### Risk Distribution in Test Data
- ~33% high-risk suppliers (late 3-14 days, 10-30% quantity shortfalls)
- ~33% medium-risk suppliers (slight delays, minor shortfalls)
- ~33% low-risk suppliers (on-time, full quantity)
