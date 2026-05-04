/**
 * Type definitions for CivilEng mobile app
 */

export type TerrainType = 'flat' | 'gentle_slope' | 'moderate_slope' | 'steep_slope' | 'hilly';
export type GroundwaterCondition = 'none_observed' | 'moist' | 'wet' | 'water_seepage' | 'standing_water';
export type BuildingType = 'residential' | 'commercial' | 'industrial' | 'infrastructure' | 'civil_works';
export type ConcreteGrade = 'C20' | 'C25' | 'C30' | 'C35' | 'C40' | 'C45' | 'C50';

export interface SitePhoto {
  id: string;
  uri: string;
  angle?: string;
  caption?: string;
  timestamp: string;
}

export interface AssessmentStep {
  id: string;
  title: string;
  description: string;
  completed: boolean;
}
