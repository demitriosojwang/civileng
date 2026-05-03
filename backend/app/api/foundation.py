"""Foundation Design API router."""

from fastapi import APIRouter
from app.calculations.foundation.bearing_capacity import (
    SoilParameters,
    FoundationGeometry,
    calculate_bearing_capacity_terzaghi,
    calculate_bearing_capacity_meyerhof,
    calculate_bearing_capacity_vesic,
)
from app.calculations.foundation.foundation_selector import (
    SiteConditions,
    BuildingParameters,
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

router = APIRouter()


@router.post("/bearing-capacity/terzaghi")
async def bearing_capacity_terzaghi(soil: SoilParameters, geometry: FoundationGeometry, fos: float = 3.0):
    """Calculate bearing capacity using Terzaghi's method."""
    return calculate_bearing_capacity_terzaghi(soil, geometry, factor_of_safety=fos)


@router.post("/bearing-capacity/meyerhof")
async def bearing_capacity_meyerhof(soil: SoilParameters, geometry: FoundationGeometry, fos: float = 3.0):
    """Calculate bearing capacity using Meyerhof's method."""
    return calculate_bearing_capacity_meyerhof(soil, geometry, factor_of_safety=fos)


@router.post("/bearing-capacity/vesic")
async def bearing_capacity_vesic(soil: SoilParameters, geometry: FoundationGeometry, fos: float = 3.0):
    """Calculate bearing capacity using Vesic's method."""
    return calculate_bearing_capacity_vesic(soil, geometry, factor_of_safety=fos)


@router.post("/recommend")
async def recommend_foundation(site: SiteConditions, building: BuildingParameters):
    """Recommend the most suitable foundation type based on site conditions."""
    return recommend_foundation_type(site, building)


@router.post("/pad", response_model=PadFoundationOutput)
async def design_pad(input_data: PadFoundationInput):
    """Design a pad foundation."""
    return design_pad_foundation(input_data)


@router.post("/strip", response_model=StripFoundationOutput)
async def design_strip(input_data: StripFoundationInput):
    """Design a strip foundation."""
    return design_strip_foundation(input_data)


@router.post("/raft", response_model=RaftFoundationOutput)
async def design_raft(input_data: RaftFoundationInput):
    """Design a raft foundation."""
    return design_raft_foundation(input_data)


@router.post("/pile", response_model=PileCapacityResult)
async def design_pile(input_data: PileInput, fos: float = 2.5):
    """Calculate pile capacity."""
    return design_pile_foundation(input_data, fos=fos)
