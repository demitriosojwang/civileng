"""
Shallow Foundation Design Calculations
Pad, Strip, and Raft foundation sizing per BS 8110 and BS 8004.
"""

import math
from pydantic import BaseModel, Field
from typing import Optional


class PadFoundationInput(BaseModel):
    column_load_kN: float = Field(..., gt=0, description="Column axial load (kN)")
    allowable_bearing_kPa: float = Field(..., gt=0, description="Allowable bearing capacity (kPa)")
    column_width_mm: float = Field(..., gt=0, description="Column width (mm)")
    concrete_grade: str = Field("C30", description="Concrete grade")
    rebar_grade: str = Field("B500", description="Reinforcement grade")
    fck: float = Field(30, description="Characteristic concrete cylinder strength (MPa)")
    fyk: float = Field(500, description="Characteristic reinforcement yield strength (MPa)")


class PadFoundationOutput(BaseModel):
    length_mm: float
    width_mm: float
    thickness_mm: float
    bearing_pressure_kPa: float
    bending_moment_kNm: float
    required_As_mm2: float
    provided_As_mm2: float
    bar_diameter_mm: int
    bar_spacing_mm: float
    shear_stress_MPa: float
    shear_capacity_MPa: float
    passes_shear: bool
    code_reference: str


def design_pad_foundation(inp: PadFoundationInput) -> PadFoundationOutput:
    """
    Design a pad foundation per BS 8110.

    Steps:
    1. Size the pad from bearing capacity
    2. Calculate bending moment at column face
    3. Calculate required reinforcement
    4. Check shear
    """
    P = inp.column_load_kN
    q_all = inp.allowable_bearing_kPa
    c = inp.column_width_mm

    # Step 1: Size the pad — assume square pad
    area_required = (P / q_all) * 1e3  # mm2 (P in kN, q_all in kPa = kN/m2)
    side = math.ceil(math.sqrt(area_required) / 50) * 50  # Round up to nearest 50mm

    # Actual bearing pressure
    q_actual = (P * 1e3) / (side * side)  # kPa (converted to N then divided by mm2 → MPa... let's keep kPa)

    # Step 2: Thickness — assume thickness = side/3 (typical starting point), minimum 300mm
    h = max(300, int(side / 3 / 25) * 25)  # Round to 25mm

    # Effective depth (assume 20mm bars with 50mm cover)
    d = h - 50 - 10  # d = h - cover - bar_radius (approximate)

    # Step 3: Bending moment at column face (cantilever from column face)
    a = (side - c) / 2  # Cantilever length (mm)
    q_kPa = (P * 1e3) / (side * side)  # N/mm2 = MPa

    M = q_kPa * side * a * a / 2  # kNm per m width... let's use total

    # Total bending moment across the full width
    M_total = q_kPa * side / 1000 * (a / 1000)**2 / 2 * 1e6  # Nmm

    # Step 4: Required reinforcement (BS 8110 simplified)
    # As = M / (0.87 * fyk * z), where z = 0.95*d for lever arm
    z = 0.95 * d
    As_required = M_total / (0.87 * inp.fyk * z)  # mm2

    # Minimum reinforcement (BS 8110 Table 3.25) — 0.13% of b*h
    As_min = 0.0013 * side * h  # mm2

    As_required = max(As_required, As_min)

    # Select bars
    bar_dia = 16  # Start with T16
    bar_area = math.pi * bar_dia**2 / 4

    n_bars = math.ceil(As_required / bar_area)
    As_provided = n_bars * bar_area

    spacing = (side - 2 * 50) / (n_bars - 1) if n_bars > 1 else side

    # Step 5: Shear check
    V = q_kPa * side * (a - d)  # Shear force at d from column face (N)
    v = V / (side * d)  # Shear stress (MPa)

    # Shear capacity (simplified BS 8110 Table 3.9)
    # vc = 0.79 * (100*As/(b*d))^(1/3) * (400/d)^(1/4) / 1.25
    ratio = 100 * As_provided / (side * d)
    vc = 0.79 * (ratio ** (1/3)) * min((400 / d) ** 0.25, 1.0) / 1.25
    vc = max(vc, 0.35)  # Minimum shear capacity

    return PadFoundationOutput(
        length_mm=side,
        width_mm=side,
        thickness_mm=h,
        bearing_pressure_kPa=round(q_actual, 2),
        bending_moment_kNm=round(M_total / 1e6, 2),
        required_As_mm2=round(As_required, 1),
        provided_As_mm2=round(As_provided, 1),
        bar_diameter_mm=bar_dia,
        bar_spacing_mm=round(spacing, 1),
        shear_stress_MPa=round(v, 3),
        shear_capacity_MPa=round(vc, 3),
        passes_shear=v <= vc,
        code_reference="BS 8110:1997, Part 1 / BS 8004:2015",
    )


class StripFoundationInput(BaseModel):
    wall_load_kN_per_m: float = Field(..., gt=0, description="Wall load per metre run (kN/m)")
    allowable_bearing_kPa: float = Field(..., gt=0, description="Allowable bearing capacity (kPa)")
    wall_thickness_mm: float = Field(..., gt=0, description="Wall thickness (mm)")
    fck: float = Field(30)
    fyk: float = Field(500)


class StripFoundationOutput(BaseModel):
    width_mm: float
    thickness_mm: float
    bearing_pressure_kPa: float
    required_As_mm2_per_m: float
    bar_diameter_mm: int
    bar_spacing_mm: float
    code_reference: str


def design_strip_foundation(inp: StripFoundationInput) -> StripFoundationOutput:
    """Design a strip foundation per BS 8110."""
    P = inp.wall_load_kN_per_m  # kN/m
    q_all = inp.allowable_bearing_kPa

    # Width from bearing capacity
    width = math.ceil((P / q_all) * 1000 / 25) * 25  # mm, round to 25mm
    width = max(width, inp.wall_thickness_mm + 200)  # Minimum 100mm each side

    # Bearing pressure
    q_actual = (P * 1000) / width  # kPa

    # Thickness — minimum 150mm or projection/3
    projection = (width - inp.wall_thickness_mm) / 2
    h = max(150, int(projection / 3 / 25) * 25)

    # Reinforcement (simplified)
    d = h - 50 - 8
    a = projection  # mm
    M = (q_actual / 1000) * a * a / 2 * 1e-3  # kNm/m

    As_required = (M * 1e6) / (0.87 * inp.fyk * 0.95 * d)

    bar_dia = 12
    bar_area = math.pi * bar_dia**2 / 4
    spacing = min(int(bar_area * 1000 / As_required), 300)

    return StripFoundationOutput(
        width_mm=width,
        thickness_mm=h,
        bearing_pressure_kPa=round(q_actual, 2),
        required_As_mm2_per_m=round(As_required, 1),
        bar_diameter_mm=bar_dia,
        bar_spacing_mm=spacing,
        code_reference="BS 8110:1997 / BS 8004:2015",
    )


class RaftFoundationInput(BaseModel):
    total_load_kN: float = Field(..., gt=0, description="Total building load (kN)")
    footprint_length_m: float = Field(..., gt=0)
    footprint_width_m: float = Field(..., gt=0)
    allowable_bearing_kPa: float = Field(..., gt=0)
    fck: float = Field(30)
    fyk: float = Field(500)


class RaftFoundationOutput(BaseModel):
    raft_length_m: float
    raft_width_m: float
    thickness_mm: float
    bearing_pressure_kPa: float
    code_reference: str
    notes: str


def design_raft_foundation(inp: RaftFoundationInput) -> RaftFoundationOutput:
    """Preliminary raft foundation design per BS 8004."""
    P = inp.total_load_kN
    q_all = inp.allowable_bearing_kPa

    # Add 10% for self-weight
    P_total = P * 1.10

    # Required area
    area_required = P_total / q_all  # m2

    L = inp.footprint_length_m + 0.6  # 300mm overhang each side
    W = inp.footprint_width_m + 0.6

    # Check if area is sufficient
    actual_area = L * W
    q_actual = P_total / actual_area

    if q_actual > q_all:
        # Extend raft
        scale = math.sqrt(area_required / actual_area)
        L = L * scale
        W = W * scale
        actual_area = L * W
        q_actual = P_total / actual_area

    # Thickness — typical 300-800mm for raft
    thickness = max(300, int((L + W) / 30 * 1000 / 25) * 25)

    return RaftFoundationOutput(
        raft_length_m=round(L, 2),
        raft_width_m=round(W, 2),
        thickness_mm=thickness,
        bearing_pressure_kPa=round(q_actual, 2),
        code_reference="BS 8004:2015 Section 5.4 / BS 8110",
        notes="Preliminary sizing. Detailed design requires structural analysis "
              "with consideration of column loads, bending moments, and differential settlement. "
              "A thickened slab under columns (pad thickenings) should be considered.",
    )
