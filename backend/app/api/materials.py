"""Material Quantities API router."""

from fastapi import APIRouter
from app.calculations.materials.boq import MaterialQuantitiesInput, calculate_material_quantities

router = APIRouter()


@router.post("/boq")
async def calculate_boq(input_data: MaterialQuantitiesInput):
    """Calculate Bill of Quantities for structural elements."""
    return calculate_material_quantities(input_data)
