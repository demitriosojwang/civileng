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
