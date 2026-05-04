/**
 * CivilEng API Service
 * Connects mobile app to the FastAPI backend.
 */

const API_BASE = __DEV__
  ? 'http://10.0.2.2:8000'  // Android emulator
  : 'https://api.civileng.app';

export interface SiteAssessmentData {
  project_name: string;
  project_id: string;
  engineer_name: string;
  assessment_date: string;
  latitude?: number;
  longitude?: number;
  location_description: string;
  terrain_type: string;
  slope_angle_deg: number;
  groundwater_condition: string;
  water_table_depth_m?: number;
  soil_color: string;
  soil_texture: string;
  soil_moisture: string;
  pct_gravel: number;
  pct_sand: number;
  pct_silt: number;
  pct_clay: number;
  pct_organic: number;
  cohesion_kPa?: number;
  angle_of_shearing_resistance_deg?: number;
  unit_weight_kN_m3?: number;
  building_type: string;
  number_of_stories: number;
  column_load_kN: number;
  total_building_load_kN: number;
  footprint_area_m2: number;
  concrete_grade: string;
  adjacent_structures: boolean;
  expansive_soil: boolean;
  seismic_zone: boolean;
}

export interface PipelineResult {
  soil_classification: any;
  bearing_capacity_terzaghi: any;
  bearing_capacity_meyerhof: any;
  bearing_capacity_vesic: any;
  recommended_bearing_capacity_kPa: number;
  foundation_recommendation: {
    recommended: string;
    alternatives: string[];
    confidence: number;
    justification: string;
    risk_factors: string[];
    cost_indicator: string;
    constructability: string;
  };
  foundation_design: Record<string, any>;
  material_quantities: any;
  warnings: string[];
  design_notes: string[];
}

export async function runPipeline(assessment: SiteAssessmentData): Promise<PipelineResult> {
  const response = await fetch(`${API_BASE}/api/reports/pipeline`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(assessment),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}

export async function classifySoil(soilData: any): Promise<any> {
  const response = await fetch(`${API_BASE}/api/soil/classify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(soilData),
  });

  if (!response.ok) throw new Error(`API error: ${response.statusText}`);
  return response.json();
}

// Offline storage — save assessments locally for sync later
const STORAGE_KEY = 'civileng_assessments';

export async function saveAssessmentOffline(assessment: SiteAssessmentData): Promise<void> {
  // Simple AsyncStorage pattern — in production use @react-native-async-storage/async-storage
  const existing = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
  existing.push({ ...assessment, savedAt: new Date().toISOString(), synced: false });
  localStorage.setItem(STORAGE_KEY, JSON.stringify(existing));
}

export async function getUnsyncedAssessments(): Promise<any[]> {
  const all = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
  return all.filter((a: any) => !a.synced);
}

export async function markAsSynced(assessmentId: string): Promise<void> {
  const all = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
  const updated = all.map((a: any) =>
    a.project_id === assessmentId ? { ...a, synced: true } : a
  );
  localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
}
