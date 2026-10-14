# VendorGuard AI — Synthetic Test Dataset

> ⚠️ **SYNTHETIC TEST DATA — NOT REAL SUPPLIER INFORMATION**
> All supplier names, locations, domains, quantities, and dates are artificially generated for local testing purposes only.

---

## Files in this folder

| File | Rows | Description |
|------|------|-------------|
| `suppliers.csv` | 100 | Supplier names, aliases, domain, location |
| `materials.csv` | 20 | Raw materials with unit and criticality |
| `supplier_materials.csv` | 45 | Which supplier provides which material + lead time |
| `purchase_order_lines.csv` | 171 | PO lines across all 50 active suppliers |
| `receipts.csv` | 159 | Delivery receipts — late/short for high-risk suppliers |
| `inventory_snapshots.csv` | 17 | Current stock levels for all materials |
| `demand_forecasts.csv` | 510 | 30-day daily demand forecast per material |

### Risk distribution in suppliers
- **High risk** (~33%): Late deliveries 3-14 days, 10-30% quantity shortfalls, some missing
- **Medium risk** (~33%): Slight delays 0-5 days, 0-10% shortfalls
- **Low risk** (~33%): On-time, full quantity, minimal rejects

---

## How to import into VendorGuard AI

**Important:** Import in this exact order — each step depends on the previous.

### Step 1 — Start the app
```powershell
cd "C:\Users\varsh\OneDrive\Documents\Desktop\scheduler\vendorguard-ai"
.\.venv\Scripts\activate
npm run dev
```
Open `http://localhost:3000`

### Step 2 — Go to Data Imports
Click **Data imports** in the left sidebar → `http://localhost:3000/imports`

### Step 3 — Import in order

For each file below, do: Select type → drag/drop CSV file → **Validate & Preview** → check for errors → **Import**

| Step | File type to select | File to upload |
|------|-------------------|----------------|
| 1 | `suppliers` | `sample-data/suppliers.csv` |
| 2 | `materials` | `sample-data/materials.csv` |
| 3 | `supplier_materials` | `sample-data/supplier_materials.csv` |
| 4 | `purchase_order_lines` | `sample-data/purchase_order_lines.csv` |
| 5 | `receipts` | `sample-data/receipts.csv` |
| 6 | `inventory_snapshots` | `sample-data/inventory_snapshots.csv` |
| 7 | `demand_forecasts` | `sample-data/demand_forecasts.csv` |

> The app will show a preview with valid/error row counts before committing.

### Step 4 — Verify data is loaded
- `http://localhost:3000/suppliers` — should show 100 suppliers with risk scores
- `http://localhost:3000/materials` — should show 20 materials with stock levels
- `http://localhost:3000/alerts` — high-risk suppliers should appear here
- `http://127.0.0.1:8000/api/suppliers` — raw JSON from backend

---

## Column reference

### suppliers.csv
```
legal_name, aliases, domain, location
```
- `aliases`: semicolon-separated e.g. `Apex Poly;Apex Chem`

### materials.csv
```
name, canonical_unit, criticality
```
- `canonical_unit`: `kg`, `rolls`, `units`, `litre`
- `criticality`: `tier_1`, `tier_2`, `tier_3`

### supplier_materials.csv
```
supplier_name, material_name, normal_lead_time_days, is_approved
```
- `supplier_name` must match an existing supplier's `legal_name`
- `material_name` must match an existing material's `name`

### purchase_order_lines.csv
```
po_number, line_number, supplier_name, material_name, ordered_quantity, unit, committed_due_date
```
- `committed_due_date` format: `YYYY-MM-DD`

### receipts.csv
```
po_number, line_number, accepted_quantity, rejected_quantity, received_at
```
- `received_at` format: `YYYY-MM-DDTHH:MM:SSZ`

### inventory_snapshots.csv
```
material_name, warehouse, on_hand_quantity, reserved_quantity, observed_at
```

### demand_forecasts.csv
```
material_name, date, daily_quantity
```
- `date` format: `YYYY-MM-DD`
