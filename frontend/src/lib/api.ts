/**
 * CivilEng API Client
 * Connects the frontend dashboard to the FastAPI backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface SoilParams {
  cohesion: number;
  angle_of_shearing_resistance: number;
  unit_weight: number;
  water_table_depth?: number;
  saturated_unit_weight?: number;
}

export interface FoundationGeometry {
  width: number;
  length?: number;
  depth: number;
}

export interface BearingCapacityResult {
  method: string;
  ultimate_bearing_capacity: number;
  net_ultimate_bearing_capacity: number;
  allowable_bearing_capacity: number;
  factor_of_safety: number;
  code_reference: string;
  intermediate_steps: Record<string, number>;
}

export interface FoundationRecommendation {
  recommended: string;
  alternatives: string[];
  confidence: number;
  justification: string;
  risk_factors: string[];
  code_references: string[];
  cost_indicator: string;
  constructability: string;
}

export interface PipelineResult {
  soil_classification: any;
  bearing_capacity_terzaghi: BearingCapacityResult;
  bearing_capacity_meyerhof: BearingCapacityResult;
  bearing_capacity_vesic: BearingCapacityResult;
  recommended_bearing_capacity_kPa: number;
  foundation_recommendation: FoundationRecommendation;
  foundation_design: Record<string, any>;
  material_quantities: any;
  warnings: string[];
  design_notes: string[];
}

// ─── API Functions ───

export async function calculateBearingCapacity(
  method: 'terzaghi' | 'meyerhof' | 'vesic',
  soil: SoilParams,
  geometry: FoundationGeometry,
  fos: number = 3.0
): Promise<BearingCapacityResult> {
  const res = await fetch(`${API_BASE}/api/foundation/bearing-capacity/${method}?fos=${fos}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(soil),
  });
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return res.json();
}

export async function recommendFoundation(
  site: any,
  building: any
): Promise<FoundationRecommendation> {
  const res = await fetch(`${API_BASE}/api/foundation/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ site, building }),
  });
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return res.json();
}

export async function runFullPipeline(
  assessment: any
): Promise<PipelineResult> {
  const res = await fetch(`${API_BASE}/api/reports/pipeline`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(assessment),
  });
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return res.json();
}

export async function generateReportPDF(
  assessment: any
): Promise<Blob> {
  const res = await fetch(`${API_BASE}/api/reports/foundation/pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(assessment),
  });
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return res.blob();
}

export async function classifySoil(soilData: any): Promise<any> {
  const res = await fetch(`${API_BASE}/api/soil/classify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(soilData),
  });
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return res.json();
}

export async function getSupportedStandards(): Promise<any> {
  const res = await fetch(`${API_BASE}/api/standards`);
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return res.json();
}

export async function healthCheck(): Promise<any> {
  const res = await fetch(`${API_BASE}/api/health`);
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return res.json();
}


// ─── Moderation API ───

export interface ModerationStats {
  reviews_pending: number;
  reviews_in_review: number;
  reviews_approved_today: number;
  reviews_rejected_today: number;
  reviews_total: number;
  disputes_open: number;
  disputes_investigating: number;
  disputes_resolved_today: number;
  disputes_critical: number;
  disputes_total: number;
  blacklist_active: number;
  blacklist_pending_approval: number;
  blacklist_banned: number;
  blacklist_total: number;
  recent_activity: { type: string; id: string; description: string; timestamp: string }[];
}

export async function getModerationStats(): Promise<ModerationStats> {
  const res = await fetch(`${API_BASE}/api/moderation/stats`);
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return res.json();
}

// Reviews
export async function listReviews(filters?: { status?: string; priority?: string; review_type?: string; limit?: number; offset?: number }): Promise<{ items: any[]; total: number }> {
  const params = new URLSearchParams();
  if (filters?.status) params.set("status", filters.status);
  if (filters?.priority) params.set("priority", filters.priority);
  if (filters?.review_type) params.set("review_type", filters.review_type);
  if (filters?.limit) params.set("limit", filters.limit.toString());
  if (filters?.offset) params.set("offset", filters.offset.toString());
  const res = await fetch(`${API_BASE}/api/moderation/reviews?${params}`);
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return res.json();
}

export async function createReview(data: any): Promise<any> {
  const res = await fetch(`${API_BASE}/api/moderation/reviews`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return res.json();
}

export async function getReview(reviewId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/moderation/reviews/${reviewId}`);
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return res.json();
}

export async function addReviewAction(reviewId: string, action: string, comment: string = "", adminId: string = "admin_001"): Promise<any> {
  const res = await fetch(`${API_BASE}/api/moderation/reviews/${reviewId}/actions?admin_id=${adminId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, comment }),
  });
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return res.json();
}

// Disputes
export async function listDisputes(filters?: { status?: string; severity?: string; dispute_type?: string; limit?: number; offset?: number }): Promise<{ items: any[]; total: number }> {
  const params = new URLSearchParams();
  if (filters?.status) params.set("status", filters.status);
  if (filters?.severity) params.set("severity", filters.severity);
  if (filters?.dispute_type) params.set("dispute_type", filters.dispute_type);
  const res = await fetch(`${API_BASE}/api/moderation/disputes?${params}`);
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return res.json();
}

export async function createDispute(data: any): Promise<any> {
  const res = await fetch(`${API_BASE}/api/moderation/disputes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return res.json();
}

export async function addDisputeComment(disputeId: string, comment: string, authorName: string, isInternal: boolean = false): Promise<any> {
  const res = await fetch(`${API_BASE}/api/moderation/disputes/${disputeId}/comments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ comment, author_name: authorName, author_role: "admin", is_internal: isInternal }),
  });
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return res.json();
}

// Blacklist
export async function listBlacklist(filters?: { entity_type?: string; severity?: string; reason_category?: string; is_active?: boolean; search?: string; limit?: number; offset?: number }): Promise<{ items: any[]; total: number }> {
  const params = new URLSearchParams();
  if (filters?.entity_type) params.set("entity_type", filters.entity_type);
  if (filters?.severity) params.set("severity", filters.severity);
  if (filters?.reason_category) params.set("reason_category", filters.reason_category);
  if (filters?.is_active !== undefined) params.set("is_active", filters.is_active.toString());
  if (filters?.search) params.set("search", filters.search);
  const res = await fetch(`${API_BASE}/api/moderation/blacklist?${params}`);
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return res.json();
}

export async function addBlacklistEntry(data: any): Promise<any> {
  const res = await fetch(`${API_BASE}/api/moderation/blacklist`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return res.json();
}

export async function checkBlacklist(entityName: string, registrationNumber: string = ""): Promise<{ entity_name: string; is_blacklisted: boolean; matches: any[] }> {
  const params = new URLSearchParams({ entity_name: entityName });
  if (registrationNumber) params.set("registration_number", registrationNumber);
  const res = await fetch(`${API_BASE}/api/moderation/blacklist/check?${params}`);
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return res.json();
}
