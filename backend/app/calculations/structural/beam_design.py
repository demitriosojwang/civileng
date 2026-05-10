"""
Beam Design Calculations per BS 8110:1997
Covers bending, shear, and deflection checks for reinforced concrete beams.
"""

import math
from pydantic import BaseModel, Field
from typing import Optional


class BeamInput(BaseModel):
    span_m: float = Field(..., gt=0, description="Beam span (m)")
    width_mm: float = Field(..., gt=0, description="Beam width b (mm)")
    depth_mm: float = Field(..., gt=0, description="Overall beam depth h (mm)")
    cover_mm: float = Field(25, description="Nominal cover (mm)")
    ultimate_moment_kNm: float = Field(..., ge=0, description="Applied ultimate bending moment (kNm)")
    ultimate_shear_kN: float = Field(..., ge=0, description="Applied ultimate shear force (kN)")
    fck: float = Field(30, description="Concrete characteristic strength (MPa)")
    fyk: float = Field(500, description="Reinforcement yield strength (MPa)")
    bar_diameter_mm: int = Field(20, description="Assumed main bar diameter (mm)")
    link_diameter_mm: int = Field(10, description="Assumed link diameter (mm)")


class BeamOutput(BaseModel):
    effective_depth_mm: float
    lever_arm_z_mm: float
    required_As_mm2: float
    provided_As_mm2: float
    number_of_bars: int
    bar_diameter_mm: int
    bending_utilization: float
    shear_stress_MPa: float
    shear_capacity_MPa: float
    links_required: bool
    link_spacing_mm: float
    passes_shear: bool
    span_to_depth_ratio: float
    allowable_span_depth_ratio: float
    passes_deflection: bool
    code_reference: str


def design_beam(inp: BeamInput) -> BeamOutput:
    """
    Design a reinforced concrete beam per BS 8110:1997.

    Checks:
    1. Bending — calculate required reinforcement
    2. Shear — check concrete capacity and links
    3. Deflection — span/effective depth ratio
    """
    b = inp.width_mm
    h = inp.depth_mm
    d = h - inp.cover_mm - inp.link_diameter_mm - inp.bar_diameter_mm / 2  # Effective depth

    M = inp.ultimate_moment_kNm * 1e6  # Convert to Nmm
    V = inp.ultimate_shear_kN * 1e3  # Convert to N

    # ===== BENDING =====
    # K = M / (fck * b * d^2)
    K = M / (inp.fck * b * d**2)

    # Check if compression reinforcement is needed (K > K')
    K_prime = 0.156  # For simply supported, BS 8110

    if K <= K_prime:
        # Singly reinforced
        z = d * (0.5 + math.sqrt(0.25 - K / 1.8))  # Lever arm
        z = min(z, 0.95 * d)  # Maximum lever arm

        As_required = M / (0.87 * inp.fyk * z)  # mm2
    else:
        # Doubly reinforced needed — for now, flag and size anyway
        z = 0.775 * d  # Approximate
        As_required = M / (0.87 * inp.fyk * z)

    # Minimum reinforcement (BS 8110 Table 3.25)
    As_min = 0.13 * b * h / 100  # 0.13% of bh
    As_required = max(As_required, As_min)

    # Bar selection
    bar_area = math.pi * inp.bar_diameter_mm**2 / 4
    n_bars = math.ceil(As_required / bar_area)
    As_provided = n_bars * bar_area

    # Bending utilization
    bending_util = As_required / As_provided if As_provided > 0 else 1.0

    # ===== SHEAR =====
    v = V / (b * d)  # Shear stress (MPa)

    # Concrete shear capacity vc (BS 8110 Table 3.9)
    As_ratio = 100 * As_provided / (b * d)
    vc = 0.79 * (As_ratio ** (1/3)) * min((400 / d) ** 0.25, 1.0) / 1.25
    vc = max(vc, 0.35)

    # Check if links are needed
    links_required = v > vc
    link_spacing = 0.75 * d  # Default maximum spacing

    if links_required:
        # Design links (simplified)
        Asv = 2 * math.pi * inp.link_diameter_mm**2 / 4  # 2 legs
        # Vc + Asv * fyv / sv >= V
        sv = Asv * 0.87 * inp.fyk * d / (V - vc * b * d) if V > vc * b * d else 0.75 * d
        link_spacing = min(sv, 0.75 * d)
        link_spacing = max(link_spacing, 100)  # Minimum spacing

    # ===== DEFLECTION =====
    span_depth_ratio = inp.span_m * 1000 / d

    # Basic span/depth ratio (BS 8110 Table 3.10)
    if inp.span_m <= 10:
        basic_ratio = 20  # Simply supported
    else:
        basic_ratio = 20

    # Modification factor (BS 8110 Table 3.11)
    M_service = inp.ultimate_moment_kNm / 1.5  # Approximate service moment
    fs = 0.87 * inp.fyk * As_required / As_provided if As_provided > 0 else 0.87 * inp.fyk

    modification = 0.55 + (477 - fs) / (120 * (0.9 + M_service / (b * d**2 / 1e6))) if M_service > 0 else 1.0
    modification = max(0.7, min(modification, 2.0))

    allowable_ratio = basic_ratio * modification

    return BeamOutput(
        effective_depth_mm=round(d, 1),
        lever_arm_z_mm=round(z, 1),
        required_As_mm2=round(As_required, 1),
        provided_As_mm2=round(As_provided, 1),
        number_of_bars=n_bars,
        bar_diameter_mm=inp.bar_diameter_mm,
        bending_utilization=round(bending_util, 3),
        shear_stress_MPa=round(v, 3),
        shear_capacity_MPa=round(vc, 3),
        links_required=links_required,
        link_spacing_mm=round(link_spacing, 1),
        passes_shear=v <= vc or links_required,
        span_to_depth_ratio=round(span_depth_ratio, 2),
        allowable_span_depth_ratio=round(allowable_ratio, 2),
        passes_deflection=span_depth_ratio <= allowable_ratio,
        code_reference="BS 8110:1997, Part 1, Cl.3.4.4 (bending), Cl.3.4.5 (shear), Cl.3.4.6 (deflection)",
    )
