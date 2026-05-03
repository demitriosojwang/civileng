"""
Soil Classification per BS 5930 / ISO 14688
Classifies soil based on particle size distribution and plasticity characteristics.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class SoilGroup(str, Enum):
    """BS 5930 soil groups."""
    BOULDERS = "boulders"
    COBBLES = "cobbles"
    GRAVEL = "gravel"
    SAND = "sand"
    SILT = "silt"
    CLAY = "clay"
    ORGANIC = "organic"
    PEAT = "peat"
    FILL = "fill"


class SoilClassificationInput(BaseModel):
    """Input parameters for soil classification."""
    # Particle size distribution (% passing)
    percent_coarse_gravel: float = Field(0, ge=0, le=100, description="% coarse gravel (>20mm)")
    percent_fine_gravel: float = Field(0, ge=0, le=100, description="% fine gravel (2-20mm)")
    percent_coarse_sand: float = Field(0, ge=0, le=100, description="% coarse sand (0.6-2mm)")
    percent_medium_sand: float = Field(0, ge=0, le=100, description="% medium sand (0.2-0.6mm)")
    percent_fine_sand: float = Field(0, ge=0, le=100, description="% fine sand (0.06-0.2mm)")
    percent_silt: float = Field(0, ge=0, le=100, description="% silt (0.002-0.06mm)")
    percent_clay: float = Field(0, ge=0, le=100, description="% clay (<0.002mm)")
    percent_organic: float = Field(0, ge=0, le=100, description="% organic matter")

    # Plasticity (Atterberg limits)
    liquid_limit: Optional[float] = Field(None, ge=0, le=200, description="Liquid limit LL (%)")
    plastic_limit: Optional[float] = Field(None, ge=0, le=200, description="Plastic limit PL (%)")
    plasticity_index: Optional[float] = Field(None, ge=0, description="Plasticity index PI = LL - PL (%)")

    # Other
    moisture_content: Optional[float] = Field(None, ge=0, le=200, description="Natural moisture content (%)")
    color: Optional[str] = Field(None, description="Soil color description")
    description: Optional[str] = Field(None, description="Free-form soil description")


class SoilClassificationResult(BaseModel):
    """Soil classification result."""
    primary_group: SoilGroup
    secondary_group: Optional[SoilGroup]
    bs5930_name: str
    is_fine_grained: bool
    coarse_fraction_pct: float
    fine_fraction_pct: float
    plasticity: Optional[str]
    estimated_bearing_capacity_kPa: float
    estimated_angle_of_shearing_resistance_deg: Optional[float]
    estimated_cohesion_kPa: Optional[float]
    suitability_notes: list
    code_reference: str


def classify_soil(inp: SoilClassificationInput) -> SoilClassificationResult:
    """
    Classify soil per BS 5930:2015 + Code of practice for ground investigations.

    Classification logic:
    1. Check organic content first
    2. Determine coarse vs fine fraction (>0.06mm vs <0.06mm)
    3. If coarse fraction dominates (>50%) — classify as granular
    4. If fine fraction dominates (>50%) — classify by plasticity
    """
    # Check organic
    if inp.percent_organic > 20:
        return _organic_classification(inp)

    # Coarse vs fine fraction
    coarse = (inp.percent_coarse_gravel + inp.percent_fine_gravel +
              inp.percent_coarse_sand + inp.percent_medium_sand + inp.percent_fine_sand)
    fine = inp.percent_silt + inp.percent_clay

    if coarse >= 50:
        return _granular_classification(inp, coarse, fine)
    else:
        return _fine_classification(inp, coarse, fine)


def _organic_classification(inp: SoilClassificationInput) -> SoilClassificationResult:
    """Classify organic soils."""
    return SoilClassificationResult(
        primary_group=SoilGroup.ORGANIC,
        secondary_group=SoilGroup.PEAT if inp.percent_organic > 50 else None,
        bs5930_name=f"{'Peat' if inp.percent_organic > 50 else 'Organic soil'}",
        is_fine_grained=True,
        coarse_fraction_pct=0,
        fine_fraction_pct=100,
        plasticity=None,
        estimated_bearing_capacity_kPa=25,
        estimated_angle_of_shearing_resistance_deg=None,
        estimated_cohesion_kPa=10,
        suitability_notes=[
            "Organic soils are unsuitable for shallow foundations",
            "Pile foundations to competent stratum required",
            "High compressibility — long-term settlement expected",
            "Not suitable as engineered fill",
        ],
        code_reference="BS 5930:2015 Section 6 / ISO 14688-1",
    )


def _granular_classification(inp: SoilClassificationInput, coarse: float, fine: float) -> SoilClassificationResult:
    """Classify granular (coarse-grained) soils."""
    # Determine dominant coarse fraction
    gravel = inp.percent_coarse_gravel + inp.percent_fine_gravel
    sand = inp.percent_coarse_sand + inp.percent_medium_sand + inp.percent_fine_sand

    if gravel > sand:
        primary = SoilGroup.GRAVEL
        name_prefix = "Gravel"
    else:
        primary = SoilGroup.SAND
        name_prefix = "Sand"

    # Adjective for fine content
    if fine > 15:
        adjective = "silty" if inp.percent_silt > inp.percent_clay else "clayey"
        secondary = SoilGroup.SILT if inp.percent_silt > inp.percent_clay else SoilGroup.CLAY
    else:
        adjective = "clean"
        secondary = None

    name = f"{adjective} {name_prefix.lower()}" if fine > 15 else name_prefix

    # Estimate engineering properties
    if primary == SoilGroup.GRAVEL:
        if fine < 5:
            bc = 300
            phi = 38
        elif fine < 15:
            bc = 200
            phi = 34
        else:
            bc = 150
            phi = 30
    else:  # Sand
        if fine < 5:
            bc = 200
            phi = 35
        elif fine < 15:
            bc = 150
            phi = 32
        else:
            bc = 100
            phi = 28

    return SoilClassificationResult(
        primary_group=primary,
        secondary_group=secondary,
        bs5930_name=f"{name.capitalize()} (BS 5930)",
        is_fine_grained=False,
        coarse_fraction_pct=round(coarse, 1),
        fine_fraction_pct=round(fine, 1),
        plasticity=None,
        estimated_bearing_capacity_kPa=bc,
        estimated_angle_of_shearing_resistance_deg=phi,
        estimated_cohesion_kPa=0,
        suitability_notes=[
            f"Granular soil with estimated bearing capacity {bc} kPa",
            "Good drainage characteristics",
            "Bearing capacity increases with depth of embedment",
            "Check for loose conditions — SPT N-value recommended",
        ],
        code_reference="BS 5930:2015 Section 6 / ISO 14688-1",
    )


def _fine_classification(inp: SoilClassificationInput, coarse: float, fine: float) -> SoilClassificationResult:
    """Classify fine-grained soils by plasticity."""
    # Determine silt vs clay
    if inp.percent_clay > inp.percent_silt:
        primary = SoilGroup.CLAY
        secondary = SoilGroup.SILT if inp.percent_silt > 15 else None
    else:
        primary = SoilGroup.SILT
        secondary = SoilGroup.CLAY if inp.percent_clay > 15 else None

    # Plasticity classification
    PI = inp.plasticity_index
    LL = inp.liquid_limit

    if PI is not None:
        if PI < 7:
            plasticity = "Low"
        elif PI < 20:
            plasticity = "Medium"
        elif PI < 40:
            plasticity = "High"
        else:
            plasticity = "Very High"
    else:
        plasticity = "Unknown"

    # Estimate engineering properties based on plasticity
    if primary == SoilGroup.CLAY:
        if plasticity == "Low":
            bc, cu = 150, 50
        elif plasticity == "Medium":
            bc, cu = 100, 40
        elif plasticity == "High":
            bc, cu = 75, 30
        elif plasticity == "Very High":
            bc, cu = 50, 25
        else:
            bc, cu = 100, 40

        notes = [
            f"Clay soil with {plasticity.lower()} plasticity",
            f"Estimated undrained cohesion: {cu} kPa",
            "Consolidation settlement must be checked",
            "May be susceptible to shrinkage/swelling if PI > 20",
        ]
    else:
        bc = 75
        cu = 25
        notes = [
            "Silt soil — susceptible to frost heave in cold climates",
            "Low permeability — drainage may be an issue",
            "Check for quick condition if loose and saturated",
        ]

    return SoilClassificationResult(
        primary_group=primary,
        secondary_group=secondary,
        bs5930_name=f"{primary.value.capitalize()} ({plasticity} plasticity)",
        is_fine_grained=True,
        coarse_fraction_pct=round(coarse, 1),
        fine_fraction_pct=round(fine, 1),
        plasticity=plasticity,
        estimated_bearing_capacity_kPa=bc,
        estimated_angle_of_shearing_resistance_deg=None,
        estimated_cohesion_kPa=cu,
        suitability_notes=notes,
        code_reference="BS 5930:2015 Section 6 / ISO 14688-1",
    )
