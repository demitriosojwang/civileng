"""
Site Assessment → Calculation Pipeline
Transforms site capture data into calculation engine inputs and runs the full design workflow.

This is the core pipeline that makes CivilEng work end-to-end:
  Site Photos + Forms → Soil Classification → Bearing Capacity → Foundation Type → Foundation Design → BOQ

Reference: Phase 2.3 — Site Data → Calculation Pipeline
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

from app.calculations.soil.classifier import (
    SoilClassificationInput,
    SoilClassificationResult,
    classify_soil,
)
from app.calculations.foundation.bearing_capacity import (
    SoilParameters,
    FoundationGeometry,
    BearingCapacityResult,
    calculate_bearing_capacity_terzaghi,
    calculate_bearing_capacity_meyerhof,
    calculate_bearing_capacity_vesic,
)
from app.calculations.foundation.foundation_selector import (
    SiteConditions,
    BuildingParameters,
    SoilCategory,
    BuildingType,
    FoundationRecommendation,
    recommend_foundation_type,
)
from app.calculations.foundation.shallow_foundations import (
    PadFoundationInput,
    PadFoundationOutput,
    StripFoundationInput,
    StripFoundationOutput,
    RaftFoundationInput,
    RaftFoundationOutput,
    design_pad_foundation,
    design_strip_foundation,
    design_raft_foundation,
)
from app.calculations.foundation.pile_foundations import (
    PileInput,
    PileCapacityResult,
    design_pile_foundation,
)
from app.calculations.materials.boq import (
    MaterialQuantitiesInput,
    MaterialQuantitiesResult,
    FoundationBOQ,
    calculate_material_quantities,
)


# ─── Site Assessment Input (from mobile capture) ───

class TerrainType(str, Enum):
    FLAT = "flat"
    GENTLE_SLOPE = "gentle_slope"
    MODERATE_SLOPE = "moderate_slope"
    STEEP_SLOPE = "steep_slope"
    HILLY = "hilly"


class GroundwaterCondition(str, Enum):
    NONE_OBSERVED = "none_observed"
    MOIST = "moist"
    WET = "wet"
    WATER_SEEPAGE = "water_seepage"
    STANDING_WATER = "standing_water"


class AdjacentStructureCondition(str, Enum):
    NONE = "none"
    SOUND = "sound"
    MINOR_CRACKS = "minor_cracks"
    SIGNIFICANT_CRACKS = "significant_cracks"
    SETTLEMENT_SIGNS = "settlement_signs"


class SiteAssessmentInput(BaseModel):
    """Full site assessment data captured from mobile app."""
    # Project info
    project_name: str
    project_id: str
    engineer_name: str
    assessment_date: str

    # Location
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_description: str = ""

    # Terrain
    terrain_type: TerrainType = TerrainType.FLAT
    slope_angle_deg: float = Field(0, ge=0, le=90)
    slope_direction: Optional[str] = None

    # Groundwater
    groundwater_condition: GroundwaterCondition = GroundwaterCondition.NONE_OBSERVED
    water_table_depth_m: Optional[float] = None
    drainage_description: str = ""

    # Soil visual assessment
    soil_color: str = ""
    soil_texture: str = Field("", description="e.g., sandy, clayey, silty, gravelly")
    soil_moisture: str = Field("", description="e.g., dry, moist, wet, saturated")
    soil_layering_observed: bool = False
    soil_layer_description: str = Field("", description="Description of visible soil layers")
    rock_outcrops: bool = False
    rock_type: Optional[str] = None

    # Soil parameters (if field tests were done)
    spt_n_values: Optional[List[int]] = None
    cohesion_kPa: Optional[float] = None
    angle_of_shearing_resistance_deg: Optional[float] = None
    unit_weight_kN_m3: Optional[float] = None
    liquid_limit_pct: Optional[float] = None
    plastic_limit_pct: Optional[float] = None

    # Particle size distribution (if lab test available)
    pct_gravel: float = 0
    pct_sand: float = 0
    pct_silt: float = 0
    pct_clay: float = 0
    pct_organic: float = 0

    # Adjacent structures
    adjacent_structures: bool = False
    adjacent_condition: AdjacentStructureCondition = AdjacentStructureCondition.NONE
    adjacent_description: str = ""

    # Environmental flags
    expansive_soil: bool = False
    seismic_zone: bool = False
    frost susceptible: bool = False

    # Access and logistics
    access_road_type: str = ""
    site_access_notes: str = ""

    # Photos (references — actual files stored separately)
    photo_ids: List[str] = []

    # Building parameters
    building_type: BuildingType = BuildingType.RESIDENTIAL
    number_of_stories: int = Field(1, ge=1)
    column_load_kN: float = Field(500, gt=0)
    total_building_load_kN: float = Field(5000, gt=0)
    footprint_area_m2: float = Field(200, gt=0)
    footprint_length_m: Optional[float] = None
    footprint_width_m: Optional[float] = None

    # Design preferences
    preferred_foundation_type: Optional[str] = None
    concrete_grade: str = "C30"
    rebar_grade: str = "B500"


# ─── Pipeline Output ───

class SiteAssessmentPipelineResult(BaseModel):
    """Complete pipeline output — from site assessment to design recommendations."""
    # Step 1: Soil Classification
    soil_classification: SoilClassificationResult

    # Step 2: Bearing Capacity (all three methods)
    bearing_capacity_terzaghi: BearingCapacityResult
    bearing_capacity_meyerhof: BearingCapacityResult
    bearing_capacity_vesic: BearingCapacityResult
    recommended_bearing_capacity_kPa: float

    # Step 3: Foundation Type Recommendation
    foundation_recommendation: FoundationRecommendation

    # Step 4: Foundation Design (whichever type was recommended)
    foundation_design: dict  # Varies by type

    # Step 5: Material Quantities
    material_quantities: MaterialQuantitiesResult

    # Warnings and notes
    warnings: List[str]
    design_notes: List[str]


# ─── Soil Category Mapping ───

def _map_soil_category(soil_result: SoilClassificationResult) -> SoilCategory:
    """Map BS 5930 soil classification to foundation selector soil category."""
    mapping = {
        "rock": SoilCategory.ROCK,
        "granular_dense": SoilCategory.GRANULAR_DENSE,
        "granular_medium": SoilCategory.GRANULAR_MEDIUM,
        "granular_loose": SoilCategory.GRANULAR_LOOSE,
        "clay_stiff": SoilCategory.CLAY_STIFF,
        "clay_firm": SoilCategory.CLAY_FIRM,
        "clay_soft": SoilCategory.CLAY_SOFT,
        "organic": SoilCategory.ORGANIC,
        "fill_made_ground": SoilCategory.FILL_MADE_GROUND,
    }
    # Determine from classification
    if soil_result.primary_group.value == "rock":
        return SoilCategory.ROCK

    bc = soil_result.estimated_bearing_capacity_kPa

    if soil_result.primary_group.value in ("gravel", "sand"):
        if bc >= 250:
            return SoilCategory.GRANULAR_DENSE
        elif bc >= 100:
            return SoilCategory.GRANULAR_MEDIUM
        else:
            return SoilCategory.GRANULAR_LOOSE

    if soil_result.primary_group.value == "clay":
        if bc >= 150:
            return SoilCategory.CLAY_STIFF
        elif bc >= 75:
            return SoilCategory.CLAY_FIRM
        else:
            return SoilCategory.CLAY_SOFT

    if soil_result.primary_group.value in ("organic", "peat"):
        return SoilCategory.ORGANIC

    return SoilCategory.GRANULAR_MEDIUM  # Default


# ─── Main Pipeline ───

def run_site_assessment_pipeline(assessment: SiteAssessmentInput) -> SiteAssessmentPipelineResult:
    """
    Run the complete site assessment → design pipeline.

    Steps:
    1. Classify soil from visual/lab data
    2. Calculate bearing capacity using all three methods
    3. Recommend foundation type
    4. Design the recommended foundation
    5. Calculate material quantities (BOQ)
    """
    warnings = []
    design_notes = []

    # ── STEP 1: Soil Classification ──
    soil_input = SoilClassificationInput(
        percent_coarse_gravel=assessment.pct_gravel * 0.4,   # Split gravel
        percent_fine_gravel=assessment.pct_gravel * 0.6,
        percent_coarse_sand=assessment.pct_sand * 0.3,       # Split sand
        percent_medium_sand=assessment.pct_sand * 0.4,
        percent_fine_sand=assessment.pct_sand * 0.3,
        percent_silt=assessment.pct_silt,
        percent_clay=assessment.pct_clay,
        percent_organic=assessment.pct_organic,
        liquid_limit=assessment.liquid_limit_pct,
        plastic_limit=assessment.plastic_limit_pct,
        plasticity_index=(assessment.liquid_limit_pct - assessment.plastic_limit_pct)
            if assessment.liquid_limit_pct and assessment.plastic_limit_pct else None,
        moisture_content=None,
        color=assessment.soil_color,
    )

    soil_result = classify_soil(soil_input)

    design_notes.append(
        f"Soil classified as {soil_result.bs5930_name} "
        f"with estimated bearing capacity {soil_result.estimated_bearing_capacity_kPa} kPa"
    )

    # ── STEP 2: Bearing Capacity ──
    # Use provided soil parameters, or defaults from classification
    cohesion = assessment.cohesion_kPa or soil_result.estimated_cohesion_kPa or 0
    phi = (assessment.angle_of_shearing_resistance_deg or
           soil_result.estimated_angle_of_shearing_resistance_deg or 28)
    gamma = assessment.unit_weight_kN_m3 or 18

    if assessment.cohesion_kPa is None and soil_result.estimated_cohesion_kPa is not None:
        warnings.append(
            f"Cohesion estimated as {cohesion} kPa from soil classification. "
            f"Field or laboratory testing recommended for confirmation."
        )

    if assessment.angle_of_shearing_resistance_deg is None and soil_result.estimated_angle_of_shearing_resistance_deg is not None:
        warnings.append(
            f"Angle of shearing resistance estimated as {phi} degrees from soil classification. "
            f"Field or laboratory testing recommended for confirmation."
        )

    soil_params = SoilParameters(
        cohesion=cohesion,
        angle_of_shearing_resistance=phi,
        unit_weight=gamma,
        water_table_depth=assessment.water_table_depth_m,
        saturated_unit_weight=gamma + 2 if assessment.water_table_depth_m is not None else None,
    )

    # Foundation geometry — assume 2m wide, 1m deep as starting point
    geometry = FoundationGeometry(width=2.0, length=2.0, depth=1.0)

    bc_terzaghi = calculate_bearing_capacity_terzaghi(soil_params, geometry)
    bc_meyerhof = calculate_bearing_capacity_meyerhof(soil_params, geometry)
    bc_vesic = calculate_bearing_capacity_vesic(soil_params, geometry)

    # Recommended bearing capacity — take the most conservative (lowest allowable)
    recommended_bc = min(
        bc_terzaghi.allowable_bearing_capacity,
        bc_meyerhof.allowable_bearing_capacity,
        bc_vesic.allowable_bearing_capacity,
    )

    design_notes.append(
        f"Bearing capacity: Terzaghi={bc_terzaghi.allowable_bearing_capacity} kPa, "
        f"Meyerhof={bc_meyerhof.allowable_bearing_capacity} kPa, "
        f"Vesic={bc_vesic.allowable_bearing_capacity} kPa. "
        f"Using conservative value: {recommended_bc} kPa"
    )

    # ── STEP 3: Foundation Type Recommendation ──
    soil_category = _map_soil_category(soil_result)

    site_conditions = SiteConditions(
        soil_category=soil_category,
        bearing_capacity_kPa=recommended_bc,
        water_table_depth_m=assessment.water_table_depth_m,
        slope_angle_deg=assessment.slope_angle_deg,
        adjacent_structures=assessment.adjacent_structures,
        expansive_soil=assessment.expansive_soil,
        seismic_zone=assessment.seismic_zone,
    )

    building_params = BuildingParameters(
        building_type=assessment.building_type,
        number_of_stories=assessment.number_of_stories,
        column_load_kN=assessment.column_load_kN,
        total_building_load_kN=assessment.total_building_load_kN,
        footprint_area_m2=assessment.footprint_area_m2,
    )

    foundation_rec = recommend_foundation_type(site_conditions, building_params)

    design_notes.append(
        f"Recommended foundation: {foundation_rec.recommended.value} "
        f"(confidence: {foundation_rec.confidence:.0%}). "
        f"Justification: {foundation_rec.justification[:100]}..."
    )

    # ── STEP 4: Foundation Design ──
    foundation_design = {}
    fck = _parse_concrete_grade(assessment.concrete_grade)

    if foundation_rec.recommended.value == "pad":
        pad_input = PadFoundationInput(
            column_load_kN=assessment.column_load_kN,
            allowable_bearing_kPa=recommended_bc,
            column_width_mm=400,
            fck=fck,
        )
        pad_result = design_pad_foundation(pad_input)
        foundation_design = pad_result.dict()

        # BOQ
        n_pads = max(4, int(assessment.footprint_area_m2 / 25))  # Approximate column grid
        mat_input = MaterialQuantitiesInput(
            foundations=[FoundationBOQ(
                type="pad",
                number=n_pads,
                length_m=pad_result.length_mm / 1000,
                width_m=pad_result.width_mm / 1000,
                depth_m=pad_result.thickness_mm / 1000,
            )],
        )

    elif foundation_rec.recommended.value == "strip":
        wall_load = assessment.total_building_load_kN / (4 * math.sqrt(assessment.footprint_area_m2))  # Approximate
        strip_input = StripFoundationInput(
            wall_load_kN_per_m=wall_load,
            allowable_bearing_kPa=recommended_bc,
            wall_thickness_mm=225,
            fck=fck,
        )
        strip_result = design_strip_foundation(strip_input)
        foundation_design = strip_result.dict()

        perimeter = 4 * math.sqrt(assessment.footprint_area_m2)  # Approximate
        mat_input = MaterialQuantitiesInput(
            foundations=[FoundationBOQ(
                type="strip",
                number=1,
                length_m=perimeter,
                width_m=strip_result.width_mm / 1000,
                depth_m=strip_result.thickness_mm / 1000,
            )],
        )

    elif foundation_rec.recommended.value == "raft":
        length = assessment.footprint_length_m or math.sqrt(assessment.footprint_area_m2 * 1.5)
        width = assessment.footprint_width_m or math.sqrt(assessment.footprint_area_m2 / 1.5)
        raft_input = RaftFoundationInput(
            total_load_kN=assessment.total_building_load_kN,
            footprint_length_m=length,
            footprint_width_m=width,
            allowable_bearing_kPa=recommended_bc,
            fck=fck,
        )
        raft_result = design_raft_foundation(raft_input)
        foundation_design = raft_result.dict()

        mat_input = MaterialQuantitiesInput(
            foundations=[FoundationBOQ(
                type="raft",
                number=1,
                length_m=raft_result.raft_length_m,
                width_m=raft_result.raft_width_m,
                depth_m=raft_result.thickness_mm / 1000,
            )],
        )

    elif foundation_rec.recommended.value == "pile":
        # Default pile design
        pile_input = PileInput(
            pile_diameter_m=0.6,
            pile_length_m=15,
            soil_layers=[{
                "top_depth_m": 0,
                "bottom_depth_m": 15,
                "soil_type": "clay" if soil_result.is_fine_grained else "sand",
                "cohesion_kPa": cohesion if soil_result.is_fine_grained else None,
                "angle_of_shearing_resistance_deg": phi if not soil_result.is_fine_grained else None,
                "unit_weight_kN_m3": gamma,
            }],
            end_bearing_stratum="clay" if soil_result.is_fine_grained else "sand",
            end_bearing_cohesion_kPa=cohesion * 1.5 if soil_result.is_fine_grained else None,
            end_bearing_N_value=30 if not soil_result.is_fine_grained else None,
        )
        pile_result = design_pile_foundation(pile_input)
        foundation_design = pile_result.dict()

        n_piles = math.ceil(assessment.total_building_load_kN / pile_result.allowable_capacity_kN)
        mat_input = MaterialQuantitiesInput(
            foundations=[FoundationBOQ(
                type="pile",
                number=n_piles,
                length_m=pile_input.pile_length_m,
                width_m=pile_input.pile_diameter_m,
                depth_m=pile_input.pile_diameter_m,
            )],
        )
    else:
        mat_input = MaterialQuantitiesInput()

    # ── STEP 5: Material Quantities ──
    material_result = calculate_material_quantities(mat_input)

    design_notes.append(
        f"Total concrete: {material_result.total_concrete_with_wastage_m3} m3, "
        f"Total reinforcement: {material_result.total_rebar_with_wastage_kg} kg"
    )

    # Groundwater warnings
    if assessment.groundwater_condition in (
        GroundwaterCondition.WET,
        GroundwaterCondition.WATER_SEEPAGE,
        GroundwaterCondition.STANDING_WATER,
    ):
        warnings.append(
            f"Groundwater observed ({assessment.groundwater_condition.value}). "
            f"Dewatering may be required during construction. "
            f"Consider effect on bearing capacity and excavation stability."
        )

    # Slope warnings
    if assessment.slope_angle_deg > 15:
        warnings.append(
            f"Slope angle of {assessment.slope_angle_deg} degrees detected. "
            f"Slope stability analysis should be performed. "
            f"Foundations on or near slopes require additional consideration per BS 8004."
        )

    # Adjacent structure warnings
    if assessment.adjacent_structures and assessment.adjacent_condition in (
        AdjacentStructureCondition.SIGNIFICANT_CRACKS,
        AdjacentStructureCondition.SETTLEMENT_SIGNS,
    ):
        warnings.append(
            f"Adjacent structures show {assessment.adjacent_condition.value}. "
            f"Excavation and construction may cause further damage. "
            f"Pre-construction condition survey recommended."
        )

    return SiteAssessmentPipelineResult(
        soil_classification=soil_result,
        bearing_capacity_terzaghi=bc_terzaghi,
        bearing_capacity_meyerhof=bc_meyerhof,
        bearing_capacity_vesic=bc_vesic,
        recommended_bearing_capacity_kPa=round(recommended_bc, 2),
        foundation_recommendation=foundation_rec,
        foundation_design=foundation_design,
        material_quantities=material_result,
        warnings=warnings,
        design_notes=design_notes,
    )


def _parse_concrete_grade(grade: str) -> float:
    """Parse concrete grade string to fck value in MPa."""
    grade_map = {
        "C20": 20, "C25": 25, "C30": 30, "C35": 35,
        "C40": 40, "C45": 45, "C50": 50, "C55": 55, "C60": 60,
    }
    return grade_map.get(grade, 30)


import math
