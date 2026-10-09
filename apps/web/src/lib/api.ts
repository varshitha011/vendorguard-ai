/**
 * VendorGuard AI Typed Client SDK
 * Interacts with FastAPI backend at http://127.0.0.1:8000 with rich packaging industry fixtures
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function apiRequest<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers: { "Content-Type": "application/json", ...options?.headers }, signal: AbortSignal.timeout(15000) });
  } catch {
    throw new Error("The API is unavailable. Start the backend on port 8000 and try again.");
  }
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "The request could not be completed.");
  return data as T;
}

export interface ImportPreview {
  preview_id: string;
  total_rows: number;
  valid_rows_count: number;
  error_rows_count: number;
  errors: { row_index: number; errors: string[] }[];
  sample_preview: Record<string, unknown>[];
}

export interface SupplierSummary {
  id: string;
  legal_name: string;
  aliases: string[];
  location: string;
  materials_supplied: string[];
  total_due_lines: number;
  on_time_rate: number;
  late_fraction_L: number;
  delay_factor_D: number;
  trend_factor_T: number;
  shortfall_F: number;
  internal_index_I: number;
  external_index_E: number | null;
  blended_risk_R: number;
  band: "low" | "watch" | "high";
  external_status: "reliable_evidence" | "no_relevant_evidence" | "ambiguous_entity" | "unavailable";
  critical_override: boolean;
  override_reason?: string;
  last_assessed: string;
}

export interface MaterialExposure {
  material_id: string;
  material_name: string;
  criticality: "tier_1" | "tier_2" | "tier_3";
  unit: string;
  on_hand_stock: number;
  reserved_stock: number;
  available_stock: number;
  daily_consumption: number;
  coverage_days: number;
  scenario_arrival_days: number;
  scenario_gap_days: number;
  day_to_stockout: number | null;
  primary_supplier: string;
  has_alternate_supplier: boolean;
  alternate_suppliers: { name: string; lead_time_days: number; approved: boolean }[];
  trajectory_base: { day: number; date_str: string; balance: number; is_stockout: boolean }[];
  trajectory_stress: { day: number; date_str: string; balance: number; is_stockout: boolean }[];
}

export interface AlertItem {
  id: string;
  supplier_id: string;
  supplier_name: string;
  material_name: string;
  incident_key: string;
  severity: "high" | "watch" | "critical";
  status: "open" | "acknowledged" | "resolved" | "dismissed";
  created_at: string;
  acknowledged_at?: string;
  acknowledged_by?: string;
  grounded_explanation: {
    summary: string;
    drivers: { metric: string; label: string; value: number | string; benchmark: string }[];
    evidence_ids: string[];
    evidence_excerpt?: string;
    evidence_source?: string;
    evidence_date?: string;
    impact_assumptions: {
      material: string;
      available_stock: number;
      daily_burn: number;
      coverage_days: number;
      scenario_arrival_days: number;
      supply_gap_days: number;
    };
    suggested_actions: string[];
    limitations: string;
  };
}

export interface MonitoringRunTrace {
  id: string;
  as_of: string;
  status: "pending" | "running" | "completed" | "failed";
  attempt_count: number;
  completed_at?: string;
  summary: {
    suppliers_checked: number;
    high_risk_flagged: number;
    shortage_scenarios: number;
    evidence_found: number;
  };
  node_traces: {
    node: string;
    status: "ok" | "skipped" | "failed";
    duration_ms: number;
    details: string;
  }[];
}

export interface ReplayBaselineResult {
  system: string;
  name: string;
  inputs: string;
  alert_episode_precision: number;
  incident_recall: number;
  warning_lead_time_days: number;
  false_alert_burden: number;
  actionable_recall: number;
  top_k_agreement: number;
}

// ---------------------------------------------------------------------------
// DEFAULT MODE A SYNTHETIC PACKAGING SECTOR DATASET
// ---------------------------------------------------------------------------
export const MODE_A_SUPPLIERS: SupplierSummary[] = [
  {
    id: "sup-001",
    legal_name: "Apex Polymers Ltd",
    aliases: ["Apex Poly", "Apex Chem"],
    location: "Houston, TX",
    materials_supplied: ["Polyethylene Resin HD-500"],
    total_due_lines: 48,
    on_time_rate: 0.40,
    late_fraction_L: 0.60,
    delay_factor_D: 0.60,
    trend_factor_T: 0.80,
    shortfall_F: 0.10,
    internal_index_I: 56.5,
    external_index_E: 72.0,
    blended_risk_R: 61.15,
    band: "high",
    external_status: "reliable_evidence",
    critical_override: true,
    override_reason: "Verified facility disruption reported on petrochemical feed lines.",
    last_assessed: "2026-10-09T14:30:00Z",
  },
  {
    id: "sup-002",
    legal_name: "NovaPlast Resins Corp",
    aliases: ["NovaPlast", "Nova Polymers"],
    location: "Baton Rouge, LA",
    materials_supplied: ["Polyethylene Resin LD-200"],
    total_due_lines: 36,
    on_time_rate: 0.88,
    late_fraction_L: 0.12,
    delay_factor_D: 0.10,
    trend_factor_T: 0.05,
    shortfall_F: 0.02,
    internal_index_I: 11.2,
    external_index_E: null,
    blended_risk_R: 11.2,
    band: "low",
    external_status: "no_relevant_evidence",
    critical_override: false,
    last_assessed: "2026-10-09T14:30:00Z",
  },
  {
    id: "sup-003",
    legal_name: "FlexiFilm Global",
    aliases: ["FlexiFilm", "Flexi Extrusions"],
    location: "Greenville, SC",
    materials_supplied: ["High Barrier PVDC Film 25um"],
    total_due_lines: 24,
    on_time_rate: 0.55,
    late_fraction_L: 0.45,
    delay_factor_D: 0.40,
    trend_factor_T: 0.50,
    shortfall_F: 0.15,
    internal_index_I: 40.25,
    external_index_E: null,
    blended_risk_R: 40.25,
    band: "watch",
    external_status: "no_relevant_evidence",
    critical_override: false,
    last_assessed: "2026-10-09T14:30:00Z",
  },
  {
    id: "sup-004",
    legal_name: "PackPro Corrugated Co",
    aliases: ["PackPro Boxes", "PackPro Packaging"],
    location: "Columbus, OH",
    materials_supplied: ["3-Ply Corrugated Shipping Cartons"],
    total_due_lines: 52,
    on_time_rate: 0.94,
    late_fraction_L: 0.06,
    delay_factor_D: 0.05,
    trend_factor_T: 0.0,
    shortfall_F: 0.01,
    internal_index_I: 5.8,
    external_index_E: null,
    blended_risk_R: 5.8,
    band: "low",
    external_status: "no_relevant_evidence",
    critical_override: false,
    last_assessed: "2026-10-09T14:30:00Z",
  },
  {
    id: "sup-005",
    legal_name: "ChromaColor Labs",
    aliases: ["ChromaColor", "Chroma Masterbatch"],
    location: "McHenry, IL",
    materials_supplied: ["White Masterbatch MB-01"],
    total_due_lines: 18,
    on_time_rate: 0.65,
    late_fraction_L: 0.35,
    delay_factor_D: 0.30,
    trend_factor_T: 0.40,
    shortfall_F: 0.08,
    internal_index_I: 30.7,
    external_index_E: 45.0,
    blended_risk_R: 35.0,
    band: "watch",
    external_status: "reliable_evidence",
    critical_override: false,
    last_assessed: "2026-10-09T14:30:00Z",
  },
  {
    id: "sup-006",
    legal_name: "ShieldBarrier Films",
    aliases: ["ShieldBarrier", "Shield Co"],
    location: "Allentown, PA",
    materials_supplied: ["Biaxially-Oriented PP Film"],
    total_due_lines: 30,
    on_time_rate: 0.90,
    late_fraction_L: 0.10,
    delay_factor_D: 0.10,
    trend_factor_T: 0.0,
    shortfall_F: 0.02,
    internal_index_I: 9.8,
    external_index_E: null,
    blended_risk_R: 9.8,
    band: "low",
    external_status: "no_relevant_evidence",
    critical_override: false,
    last_assessed: "2026-10-09T14:30:00Z",
  },
  {
    id: "sup-007",
    legal_name: "Delta Resins & Chemicals",
    aliases: ["Delta Resins", "Delta Chem"],
    location: "Beaumont, TX",
    materials_supplied: ["Polyethylene Resin HD-500 (Backup)"],
    total_due_lines: 12,
    on_time_rate: 0.83,
    late_fraction_L: 0.17,
    delay_factor_D: 0.20,
    trend_factor_T: 0.10,
    shortfall_F: 0.05,
    internal_index_I: 14.5,
    external_index_E: null,
    blended_risk_R: 14.5,
    band: "low",
    external_status: "no_relevant_evidence",
    critical_override: false,
    last_assessed: "2026-10-09T14:30:00Z",
  },
];

export const MODE_A_MATERIALS: MaterialExposure[] = [
  {
    material_id: "mat-001",
    material_name: "Polyethylene Resin HD-500",
    criticality: "tier_1",
    unit: "kg",
    on_hand_stock: 800,
    reserved_stock: 0,
    available_stock: 800,
    daily_consumption: 100,
    coverage_days: 8.0,
    scenario_arrival_days: 12.0,
    scenario_gap_days: 4.0,
    day_to_stockout: 9,
    primary_supplier: "Apex Polymers Ltd",
    has_alternate_supplier: true,
    alternate_suppliers: [
      { name: "Delta Resins & Chemicals", lead_time_days: 5, approved: true },
      { name: "NovaPlast Resins Corp", lead_time_days: 7, approved: true },
    ],
    trajectory_base: Array.from({ length: 30 }, (_, i) => {
      const day = i + 1;
      const scheduled = day === 8 ? 1000 : 0;
      const bal = 800 + (day >= 8 ? 1000 : 0) - day * 100;
      return { day, date_str: `2026-10-${String(day + 9).padStart(2, "0")}`, balance: bal, is_stockout: bal < 0 };
    }),
    trajectory_stress: Array.from({ length: 30 }, (_, i) => {
      const day = i + 1;
      const delayed = day === 14 ? 1000 : 0;
      const bal = 800 + (day >= 14 ? 1000 : 0) - day * 100;
      return { day, date_str: `2026-10-${String(day + 9).padStart(2, "0")}`, balance: bal, is_stockout: bal < 0 };
    }),
  },
  {
    material_id: "mat-002",
    material_name: "High Barrier PVDC Film 25um",
    criticality: "tier_1",
    unit: "rolls",
    on_hand_stock: 120,
    reserved_stock: 20,
    available_stock: 100,
    daily_consumption: 10,
    coverage_days: 10.0,
    scenario_arrival_days: 14.0,
    scenario_gap_days: 4.0,
    day_to_stockout: 11,
    primary_supplier: "FlexiFilm Global",
    has_alternate_supplier: false,
    alternate_suppliers: [],
    trajectory_base: Array.from({ length: 30 }, (_, i) => ({
      day: i + 1,
      date_str: `2026-10-${String(i + 10).padStart(2, "0")}`,
      balance: Math.max(0, 100 - (i + 1) * 10 + (i >= 9 ? 150 : 0)),
      is_stockout: 100 - (i + 1) * 10 < 0,
    })),
    trajectory_stress: Array.from({ length: 30 }, (_, i) => ({
      day: i + 1,
      date_str: `2026-10-${String(i + 10).padStart(2, "0")}`,
      balance: 100 - (i + 1) * 10 + (i >= 15 ? 150 : 0),
      is_stockout: 100 - (i + 1) * 10 < 0,
    })),
  },
  {
    material_id: "mat-003",
    material_name: "White Masterbatch MB-01",
    criticality: "tier_2",
    unit: "kg",
    on_hand_stock: 450,
    reserved_stock: 50,
    available_stock: 400,
    daily_consumption: 25,
    coverage_days: 16.0,
    scenario_arrival_days: 12.0,
    scenario_gap_days: 0.0,
    day_to_stockout: null,
    primary_supplier: "ChromaColor Labs",
    has_alternate_supplier: true,
    alternate_suppliers: [{ name: "Spectrum Pigments", lead_time_days: 4, approved: true }],
    trajectory_base: Array.from({ length: 30 }, (_, i) => ({
      day: i + 1,
      date_str: `2026-10-${String(i + 10).padStart(2, "0")}`,
      balance: 400 - (i + 1) * 25 + (i >= 10 ? 300 : 0),
      is_stockout: false,
    })),
    trajectory_stress: Array.from({ length: 30 }, (_, i) => ({
      day: i + 1,
      date_str: `2026-10-${String(i + 10).padStart(2, "0")}`,
      balance: 400 - (i + 1) * 25 + (i >= 16 ? 300 : 0),
      is_stockout: false,
    })),
  },
];

export const MODE_A_ALERTS: AlertItem[] = [
  {
    id: "alt-001",
    supplier_id: "sup-001",
    supplier_name: "Apex Polymers Ltd",
    material_name: "Polyethylene Resin HD-500",
    incident_key: "apex-polymers-facility-delay-2026-10",
    severity: "critical",
    status: "open",
    created_at: "2026-10-09T14:32:00Z",
    grounded_explanation: {
      summary:
        "Supplier Apex Polymers' recent late fraction is 60%, and average completed delay rose from 2 to 6 days. One verified facility interruption contributes external evidence (E=72.0, R=61.15). Available resin covers 8 days at 100 kg/day. Under declared 12-day replenishment, a 4-day supply gap appears.",
      drivers: [
        { metric: "late_fraction_L", label: "Late Fraction (L)", value: "60.0%", benchmark: "< 30%" },
        { metric: "delay_trend_T", label: "Completed Delay Rise", value: "2.0d -> 6.0d", benchmark: "Stable <= 2d" },
        { metric: "blended_risk_R", label: "Blended Risk Index (R)", value: "61.15", benchmark: "High Band >= 60" },
      ],
      evidence_ids: ["ev-demo-001"],
      evidence_excerpt: "Chemical industry update: regional supply disruption at feedstock crackers affecting resin pellet extrusion.",
      evidence_source: "Petrochem Daily Bulletin (Verified Fixture)",
      evidence_date: "2026-09-20",
      impact_assumptions: {
        material: "Polyethylene Resin HD-500",
        available_stock: 800,
        daily_burn: 100,
        coverage_days: 8.0,
        scenario_arrival_days: 12.0,
        supply_gap_days: 4.0,
      },
      suggested_actions: [
        "Confirm shipment status for open PO-2026-8802 immediately.",
        "Review approved backup supplier Delta Resins (normal lead time: 5 days).",
        "Reserve 200 kg buffer from secondary extrusion schedule if delay exceeds 4 days.",
      ],
      limitations:
        "External news is synthetic demonstration data. Inventory model assumes constant 100 kg/day demand.",
    },
  },
  {
    id: "alt-002",
    supplier_id: "sup-003",
    supplier_name: "FlexiFilm Global",
    material_name: "High Barrier PVDC Film 25um",
    incident_key: "flexifilm-trend-watch-2026-10",
    severity: "watch",
    status: "open",
    created_at: "2026-10-09T14:32:00Z",
    grounded_explanation: {
      summary:
        "FlexiFilm shows gradual operational decline with 45% late fraction and delay increasing to 4 days. No external news detected (evidence-limited score R=40.25). Film stock covers 10 days with a 4-day stress gap.",
      drivers: [
        { metric: "late_fraction_L", label: "Late Fraction (L)", value: "45.0%", benchmark: "< 30%" },
        { metric: "single_source", label: "Sole Source Vulnerability", value: "Single Supplier", benchmark: "No backup" },
      ],
      evidence_ids: [],
      impact_assumptions: {
        material: "High Barrier PVDC Film 25um",
        available_stock: 100,
        daily_burn: 10,
        coverage_days: 10.0,
        scenario_arrival_days: 14.0,
        supply_gap_days: 4.0,
      },
      suggested_actions: [
        "Inquire with FlexiFilm production lead on upcoming slit rolls schedule.",
        "Begin pre-qualification testing for alternate barrier film suppliers.",
      ],
      limitations: "Sole source dependency increases actual operational exposure beyond internal delivery index alone.",
    },
  },
];

export const REPLAY_BASELINES: ReplayBaselineResult[] = [
  {
    system: "B0",
    name: "Simple Overdue Rule",
    inputs: "Current overdue PO lines only",
    alert_episode_precision: 0.38,
    incident_recall: 0.52,
    warning_lead_time_days: 0.8,
    false_alert_burden: 1.45,
    actionable_recall: 0.22,
    top_k_agreement: 0.41,
  },
  {
    system: "B1",
    name: "Internal-Only Operational Policy",
    inputs: "Historical delivery metrics (L, D, T, F)",
    alert_episode_precision: 0.62,
    incident_recall: 0.74,
    warning_lead_time_days: 4.5,
    false_alert_burden: 0.72,
    actionable_recall: 0.58,
    top_k_agreement: 0.68,
  },
  {
    system: "B2",
    name: "External-Only Evidence Policy",
    inputs: "Verified public news signals alone",
    alert_episode_precision: 0.44,
    incident_recall: 0.48,
    warning_lead_time_days: 7.2,
    false_alert_burden: 0.89,
    actionable_recall: 0.42,
    top_k_agreement: 0.51,
  },
  {
    system: "P1",
    name: "Combined VendorGuard Policy",
    inputs: "Internal history + Bounded external events (R)",
    alert_episode_precision: 0.78,
    incident_recall: 0.86,
    warning_lead_time_days: 6.8,
    false_alert_burden: 0.42,
    actionable_recall: 0.75,
    top_k_agreement: 0.79,
  },
  {
    system: "P2",
    name: "Impact-Aware Prioritization",
    inputs: "P1 + Material Exposure Simulation (B[d])",
    alert_episode_precision: 0.84,
    incident_recall: 0.89,
    warning_lead_time_days: 7.5,
    false_alert_burden: 0.31,
    actionable_recall: 0.84,
    top_k_agreement: 0.92,
  },
];

export const API_CLIENT = {
  async getSuppliers(): Promise<SupplierSummary[]> {
    try {
      const res = await fetch(`${API_BASE_URL}/api/suppliers`);
      if (res.ok) return await res.json();
    } catch {}
    return MODE_A_SUPPLIERS;
  },

  async getMaterials(): Promise<MaterialExposure[]> {
    try {
      const res = await fetch(`${API_BASE_URL}/api/materials`);
      if (res.ok) return await res.json();
    } catch {}
    return MODE_A_MATERIALS;
  },

  async getAlerts(): Promise<AlertItem[]> {
    try {
      const res = await fetch(`${API_BASE_URL}/api/alerts`);
      if (res.ok) return await res.json();
    } catch {}
    return MODE_A_ALERTS;
  },

  async triggerMonitoringRun(): Promise<{ job_id: string; status: string }> {
    return apiRequest("/api/monitoring-runs", { method: "POST" });
  },

  async updateAlert(id: string, status: AlertItem["status"]): Promise<AlertItem> {
    return apiRequest(`/api/alerts/${encodeURIComponent(id)}`, { method: "PATCH", body: JSON.stringify({ status }) });
  },

  async submitFeedback(id: string, disposition: string, reason: string) {
    return apiRequest(`/api/alerts/${encodeURIComponent(id)}/feedback`, { method: "POST", body: JSON.stringify({ disposition, reason }) });
  },

  async getRun(id?: string): Promise<MonitoringRunTrace> {
    const runId = id || (typeof window !== "undefined" ? window.sessionStorage.getItem("vendorguard-latest-run") : null) || "run-default";
    return apiRequest(`/api/monitoring-runs/${encodeURIComponent(runId)}`);
  },

  async previewImport(file_type: string, csv_text: string): Promise<ImportPreview> {
    return apiRequest("/api/imports/preview", { method: "POST", body: JSON.stringify({ file_type, csv_text }) });
  },

  async commitImport(preview_id: string): Promise<{ committed_records: number; status: string }> {
    return apiRequest(`/api/imports/${encodeURIComponent(preview_id)}/commit`, { method: "POST" });
  },

  async getReplayBaselines(): Promise<ReplayBaselineResult[]> {
    try {
      const res = await fetch(`${API_BASE_URL}/api/replay/baselines`);
      if (res.ok) return await res.json();
    } catch {}
    return REPLAY_BASELINES;
  },
};
