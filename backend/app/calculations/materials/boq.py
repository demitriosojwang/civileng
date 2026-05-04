"""
Bill of Quantities (BOQ) Calculation
Estimates concrete volumes, reinforcement weights, and formwork areas.
"""

import math
from pydantic import BaseModel, Field
from typing import List


class FoundationBOQ(BaseModel):
    """Foundation quantities."""
    type: str = Field(..., description="Foundation type: pad/strip/raft/pile")
    number: int = Field(1, description="Number of this foundation type")
    length_m: float
    width_m: float
    depth_m: float
    concrete_volume_m3: float
    rebar_weight_kg: float
    formwork_area_m2: float


class BeamBOQ(BaseModel):
    length_m: float
    width_m: float
    depth_m: float
    number: int = 1
    concrete_volume_m3: float
    rebar_weight_kg: float
    formwork_area_m2: float


class ColumnBOQ(BaseModel):
    height_m: float
    width_m: float
    depth_m: float
    number: int = 1
    concrete_volume_m3: float
    rebar_weight_kg: float
    formwork_area_m2: float


class SlabBOQ(BaseModel):
    area_m2: float
    thickness_m: float
    concrete_volume_m3: float
    rebar_weight_kg: float
    formwork_area_m2: float


class MaterialQuantitiesInput(BaseModel):
    """Input for material quantities calculation."""
    foundations: List[FoundationBOQ] = []
    beams: List[BeamBOQ] = []
    columns: List[ColumnBOQ] = []
    slabs: List[SlabBOQ] = []
    concrete_grade: str = "C30"
    wastage_pct: float = Field(5, ge=0, le=20, description="Wastage percentage for concrete")
    rebar_wastage_pct: float = Field(10, ge=0, le=25, description="Wastage percentage for reinforcement")


class MaterialQuantitiesResult(BaseModel):
    """Total material quantities."""
    total_concrete_m3: float
    total_concrete_with_wastage_m3: float
    total_rebar_kg: float
    total_rebar_with_wastage_kg: float
    total_formwork_m2: float
    foundation_quantities: List[FoundationBOQ]
    beam_quantities: List[BeamBOQ]
    column_quantities: List[ColumnBOQ]
    slab_quantities: List[SlabBOQ]
    rebar_density_kg_per_m3: float


def calculate_material_quantities(inp: MaterialQuantitiesInput) -> MaterialQuantitiesResult:
    """
    Calculate total material quantities from structural elements.

    Reinforcement density estimates (kg/m3 of concrete):
    - Pad foundations: 80-100 kg/m3
    - Strip foundations: 60-80 kg/m3
    - Raft foundations: 100-130 kg/m3
    - Pile foundations: 60-80 kg/m3
    - Beams: 120-180 kg/m3
    - Columns: 100-150 kg/m3
    - Slabs: 80-120 kg/m3
    """
    total_concrete = 0.0
    total_rebar = 0.0
    total_formwork = 0.0
    total_concrete_for_density = 0.0

    # Foundations
    found_results = []
    for f in inp.foundations:
        vol = f.length_m * f.width_m * f.depth_m * f.number
        # Reinforcement density by foundation type
        rebar_densities = {
            "pad": 90,
            "strip": 70,
            "raft": 115,
            "pile": 70,
        }
        density = rebar_densities.get(f.type, 90)
        rebar = vol * density

        # Formwork (sides + bottom minus column contact)
        fw = (2 * (f.length_m + f.width_m) * f.depth_m + f.length_m * f.width_m) * f.number

        found_results.append(FoundationBOQ(
            type=f.type,
            number=f.number,
            length_m=f.length_m,
            width_m=f.width_m,
            depth_m=f.depth_m,
            concrete_volume_m3=round(vol, 2),
            rebar_weight_kg=round(rebar, 1),
            formwork_area_m2=round(fw, 2),
        ))

        total_concrete += vol
        total_rebar += rebar
        total_formwork += fw
        total_concrete_for_density += vol

    # Beams
    beam_results = []
    for b in inp.beams:
        vol = b.length_m * b.width_m * b.depth_m * b.number
        rebar = vol * 150  # 150 kg/m3 for beams
        fw = 2 * (b.width_m + b.depth_m) * b.length_m * b.number

        beam_results.append(BeamBOQ(
            length_m=b.length_m,
            width_m=b.width_m,
            depth_m=b.depth_m,
            number=b.number,
            concrete_volume_m3=round(vol, 2),
            rebar_weight_kg=round(rebar, 1),
            formwork_area_m2=round(fw, 2),
        ))

        total_concrete += vol
        total_rebar += rebar
        total_formwork += fw
        total_concrete_for_density += vol

    # Columns
    col_results = []
    for c in inp.columns:
        vol = c.height_m * c.width_m * c.depth_m * c.number
        rebar = vol * 125  # 125 kg/m3 for columns
        fw = 2 * (c.width_m + c.depth_m) * c.height_m * c.number

        col_results.append(ColumnBOQ(
            height_m=c.height_m,
            width_m=c.width_m,
            depth_m=c.depth_m,
            number=c.number,
            concrete_volume_m3=round(vol, 2),
            rebar_weight_kg=round(rebar, 1),
            formwork_area_m2=round(fw, 2),
        ))

        total_concrete += vol
        total_rebar += rebar
        total_formwork += fw
        total_concrete_for_density += vol

    # Slabs
    slab_results = []
    for s in inp.slabs:
        vol = s.area_m2 * s.thickness_m
        rebar = vol * 100  # 100 kg/m3 for slabs
        fw = s.area_m2  # Soffit formwork only

        slab_results.append(SlabBOQ(
            area_m2=s.area_m2,
            thickness_m=s.thickness_m,
            concrete_volume_m3=round(vol, 2),
            rebar_weight_kg=round(rebar, 1),
            formwork_area_m2=round(fw, 2),
        ))

        total_concrete += vol
        total_rebar += rebar
        total_formwork += fw
        total_concrete_for_density += vol

    # Wastage
    concrete_wastage_factor = 1 + inp.wastage_pct / 100
    rebar_wastage_factor = 1 + inp.rebar_wastage_pct / 100

    # Overall rebar density
    density = total_rebar / total_concrete_for_density if total_concrete_for_density > 0 else 0

    return MaterialQuantitiesResult(
        total_concrete_m3=round(total_concrete, 2),
        total_concrete_with_wastage_m3=round(total_concrete * concrete_wastage_factor, 2),
        total_rebar_kg=round(total_rebar, 1),
        total_rebar_with_wastage_kg=round(total_rebar * rebar_wastage_factor, 1),
        total_formwork_m2=round(total_formwork, 2),
        foundation_quantities=found_results,
        beam_quantities=beam_results,
        column_quantities=col_results,
        slab_quantities=slab_results,
        rebar_density_kg_per_m3=round(density, 1),
    )
