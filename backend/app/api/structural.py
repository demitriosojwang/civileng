"""Structural Design API router."""

from fastapi import APIRouter
from app.calculations.structural.beam_design import BeamInput, design_beam
from app.calculations.structural.column_design import ColumnInput, design_column
from app.calculations.structural.load_combinations import LoadInputs, generate_load_combinations

router = APIRouter()


@router.post("/beam")
async def design_beam_endpoint(input_data: BeamInput):
    """Design a reinforced concrete beam per BS 8110."""
    return design_beam(input_data)


@router.post("/column")
async def design_column_endpoint(input_data: ColumnInput):
    """Design a reinforced concrete column per BS 8110."""
    return design_column(input_data)


@router.post("/load-combinations")
async def load_combinations(loads: LoadInputs):
    """Generate load combinations per EN 1990."""
    return generate_load_combinations(loads)
