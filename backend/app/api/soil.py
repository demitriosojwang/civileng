"""Soil Classification API router."""

from fastapi import APIRouter
from app.calculations.soil.classifier import SoilClassificationInput, classify_soil

router = APIRouter()


@router.post("/classify")
async def classify_soil_endpoint(input_data: SoilClassificationInput):
    """Classify soil per BS 5930 / ISO 14688."""
    return classify_soil(input_data)
