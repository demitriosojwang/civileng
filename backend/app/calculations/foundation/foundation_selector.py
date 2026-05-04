"""
Foundation Type Selection Engine
Decision tree for recommending the most suitable foundation type based on site conditions.

Reference: BS 8004:2015, Tomlinson's Foundation Design & Construction
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class FoundationType(str, Enum):
    PAD = "pad"
    STRIP = "strip"
    RAFT = "raft"
    PILE = "pile"


class BuildingType(str, Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    INFRASTRUCTURE = "infrastructure"
    CIVIL_WORKS = "civil_works"


class SoilCategory(str, Enum):
    ROCK = "rock"
    GRANULAR_DENSE = "granular_dense"
    GRANULAR_MEDIUM = "granular_medium"
    GRANULAR_LOOSE = "granular_loose"
    CLAY_STIFF = "clay_stiff"
    CLAY_FIRM = "clay_firm"
    CLAY_SOFT = "clay_soft"
    ORGANIC = "organic"
    FILL_MADE_GROUND = "fill_made_ground"


class SiteConditions(BaseModel):
    """Site conditions for foundation type selection."""
    soil_category: SoilCategory
    bearing_capacity_kPa: float = Field(..., description="Estimated or calculated bearing capacity (kPa)")
    water_table_depth_m: Optional[float] = Field(None, description="Depth to water table (m)")
    slope_angle_deg: float = Field(0, ge=0, le=90, description="Site slope angle (degrees)")
    adjacent_structures: bool = Field(False, description="Are there adjacent structures that may be affected?")
    expansive_soil: bool = Field(False, description="Is the soil expansive (high plasticity)?")
    seismic_zone: bool = Field(False, description="Is the site in a seismic zone?")


class BuildingParameters(BaseModel):
    """Building parameters influencing foundation selection."""
    building_type: BuildingType
    number_of_stories: int = Field(..., ge=1)
    column_load_kN: float = Field(..., gt=0, description="Maximum column axial load (kN)")
    total_building_load_kN: float = Field(..., gt=0, description="Total building load (kN)")
    footprint_area_m2: float = Field(..., gt=0, description="Building footprint area (m2)")


class FoundationRecommendation(BaseModel):
    """Foundation type recommendation with justification."""
    recommended: FoundationType
    alternatives: List[FoundationType]
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    justification: str
    risk_factors: List[str]
    code_references: List[str]
    cost_indicator: str = Field(..., description="Low / Medium / High relative cost")
    constructability: str = Field(..., description="Easy / Moderate / Difficult")


def recommend_foundation_type(
    site: SiteConditions,
    building: BuildingParameters,
) -> FoundationRecommendation:
    """
    Recommend the most suitable foundation type based on site conditions and building parameters.

    Decision logic based on BS 8004 and Tomlinson's Foundation Design & Construction.
    """
    risk_factors = []
    code_refs = ["BS 8004:2015"]

    # Determine soil bearing capacity category
    bc = site.bearing_capacity_kPa
    soil = site.soil_category

    # Check for problematic soils first
    if soil in (SoilCategory.ORGANIC, SoilCategory.FILL_MADE_GROUND):
        risk_factors.append(f"Problematic soil: {soil.value}. Pile foundation to competent stratum recommended.")
        return FoundationRecommendation(
            recommended=FoundationType.PILE,
            alternatives=[FoundationType.RAFT],
            confidence=0.90,
            justification=f"Soil category '{soil.value}' is unsuitable for shallow foundations. "
                         f"Pile foundation transferring load to competent stratum is required. "
                         f"Bearing capacity of {bc} kPa is insufficient for direct bearing.",
            risk_factors=risk_factors,
            code_references=code_refs + ["BS 8004 Section 7 (Pile foundations)"],
            cost_indicator="High",
            constructability="Difficult",
        )

    # Check for soft clay
    if soil == SoilCategory.CLAY_SOFT:
        risk_factors.append("Soft clay — excessive settlement risk with shallow foundations.")
        if site.water_table_depth_m is not None and site.water_table_depth_m < 2.0:
            risk_factors.append("High water table in soft clay — further reduces bearing capacity.")

        # For light structures, raft may work
        if building.number_of_stories <= 2 and building.column_load_kN < 300:
            return FoundationRecommendation(
                recommended=FoundationType.RAFT,
                alternatives=[FoundationType.PILE],
                confidence=0.65,
                justification=f"Soft clay with {bc} kPa bearing capacity. Raft foundation spreads load "
                             f"over the full building footprint, reducing bearing pressure. "
                             f"Settlement calculations must be performed.",
                risk_factors=risk_factors,
                code_references=code_refs + ["BS 8004 Section 5.4 (Raft foundations)"],
                cost_indicator="Medium",
                constructability="Moderate",
            )
        else:
            return FoundationRecommendation(
                recommended=FoundationType.PILE,
                alternatives=[FoundationType.RAFT],
                confidence=0.80,
                justification=f"Soft clay with {bc} kPa bearing capacity and building load of "
                             f"{building.column_load_kN} kN exceeds what shallow foundations can safely support. "
                             f"Pile foundation to competent stratum recommended.",
                risk_factors=risk_factors,
                code_references=code_refs + ["BS 8004 Section 7"],
                cost_indicator="High",
                constructability="Difficult",
            )

    # Good ground: rock, dense granular, stiff clay
    if soil in (SoilCategory.ROCK, SoilCategory.GRANULAR_DENSE, SoilCategory.CLAY_STIFF):
        # High bearing capacity — pad/strip are suitable
        if bc >= 200:
            if building.building_type in (BuildingType.RESIDENTIAL, BuildingType.COMMERCIAL) and building.number_of_stories <= 5:
                if building.column_load_kN < 2000:
                    return FoundationRecommendation(
                        recommended=FoundationType.PAD,
                        alternatives=[FoundationType.STRIP],
                        confidence=0.90,
                        justification=f"Good ground conditions ({soil.value}) with {bc} kPa bearing capacity. "
                                     f"Pad foundations are economical and suitable for the column loads "
                                     f"of {building.column_load_kN} kN.",
                        risk_factors=risk_factors or ["None significant"],
                        code_references=code_refs + ["BS 8004 Section 5.2 (Pad foundations)"],
                        cost_indicator="Low",
                        constructability="Easy",
                    )

        if building.number_of_stories > 5 or building.column_load_kN >= 2000:
            # Heavier loads — consider raft
            return FoundationRecommendation(
                recommended=FoundationType.RAFT,
                alternatives=[FoundationType.PAD, FoundationType.PILE],
                confidence=0.80,
                justification=f"Good ground but heavy loads ({building.column_load_kN} kN, "
                             f"{building.number_of_stories} stories). Raft foundation distributes "
                             f"load efficiently and reduces differential settlement risk.",
                risk_factors=risk_factors or ["Monitor differential settlement"],
                code_references=code_refs + ["BS 8004 Section 5.4"],
                cost_indicator="Medium",
                constructability="Moderate",
            )

    # Medium ground: medium granular, firm clay
    if soil in (SoilCategory.GRANULAR_MEDIUM, SoilCategory.CLAY_FIRM):
        if bc >= 100:
            if building.number_of_stories <= 3 and building.column_load_kN < 1000:
                return FoundationRecommendation(
                    recommended=FoundationType.STRIP,
                    alternatives=[FoundationType.PAD],
                    confidence=0.80,
                    justification=f"Medium ground ({soil.value}) with {bc} kPa bearing capacity. "
                                 f"Strip foundations provide good load distribution for wall loads "
                                 f"and low-rise structures.",
                    risk_factors=risk_factors or ["Check settlement"],
                    code_references=code_refs + ["BS 8004 Section 5.3 (Strip foundations)"],
                    cost_indicator="Low",
                    constructability="Easy",
                )
            else:
                return FoundationRecommendation(
                    recommended=FoundationType.RAFT,
                    alternatives=[FoundationType.PILE],
                    confidence=0.75,
                    justification=f"Medium ground with heavier loads. Raft foundation recommended "
                                 f"to spread load and minimize differential settlement.",
                    risk_factors=risk_factors + ["Settlement monitoring recommended"],
                    code_references=code_refs + ["BS 8004 Section 5.4"],
                    cost_indicator="Medium",
                    constructability="Moderate",
                )

    # Loose granular — careful
    if soil == SoilCategory.GRANULAR_LOOSE:
        risk_factors.append("Loose granular soil — vibration/compaction risk, settlement risk")
        if bc >= 75:
            return FoundationRecommendation(
                recommended=FoundationType.RAFT,
                alternatives=[FoundationType.PILE],
                confidence=0.70,
                justification=f"Loose granular soil with {bc} kPa bearing capacity. Raft foundation "
                             f"spreads load, but densification may be required.",
                risk_factors=risk_factors,
                code_references=code_refs,
                cost_indicator="Medium",
                constructability="Moderate",
            )
        else:
            return FoundationRecommendation(
                recommended=FoundationType.PILE,
                alternatives=[FoundationType.RAFT],
                confidence=0.80,
                justification=f"Loose granular soil with low bearing capacity ({bc} kPa). "
                             f"Pile foundation to denser stratum recommended.",
                risk_factors=risk_factors,
                code_references=code_refs + ["BS 8004 Section 7"],
                cost_indicator="High",
                constructability="Difficult",
            )

    # Expansive soil flag
    if site.expansive_soil:
        risk_factors.append("Expansive soil — foundation must resist heave pressures")

    # Slope consideration
    if site.slope_angle_deg > 15:
        risk_factors.append(f"Slope angle {site.slope_angle_deg} degrees — stability analysis required")

    # Default fallback
    return FoundationRecommendation(
        recommended=FoundationType.PAD,
        alternatives=[FoundationType.STRIP, FoundationType.RAFT],
        confidence=0.50,
        justification=f"Default recommendation for {soil.value} soil with {bc} kPa bearing capacity. "
                     f"Site-specific investigation should refine this recommendation.",
        risk_factors=risk_factors or ["Further site investigation recommended"],
        code_references=code_refs,
        cost_indicator="Low",
        constructability="Easy",
    )
