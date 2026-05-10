"""
Column Design Calculations per BS 8110:1997
Short braced column design for axial load with nominal eccentricity.
"""

import math
from pydantic import BaseModel, Field


class ColumnInput(BaseModel):
    axial_load_kN: float = Field(..., gt=0, description="Ultimate axial load (kN)")
    column_width_mm: float = Field(300, gt=0, description="Column width (mm)")
    column_depth_mm: float = Field(300, gt=0, description="Column depth (mm)")
    height_m: float = Field(3.0, gt=0, description="Column height (m)")
    fck: float = Field(30, description="Concrete grade (MPa)")
    fyk: float = Field(500, description="Rebar grade (MPa)")
    cover_mm: float = Field(25)


class ColumnOutput(BaseModel):
    column_width_mm: float
    column_depth_mm: float
    slenderness_ratio: float
    is_short: bool
    ultimate_capacity_kN: float
    required_Asc_mm2: float
    provided_Asc_mm2: float
    number_of_bars: int
    bar_diameter_mm: int
    links_diameter_mm: int
    link_spacing_mm: float
    utilization_ratio: float
    code_reference: str


def design_column(inp: ColumnInput) -> ColumnOutput:
    """
    Design a short braced column per BS 8110:1997, Cl.3.8.4.

    For short braced columns (lex/h <= 15, ley/b <= 15):
    N = 0.4 * fck * Ac + 0.67 * fck * Asc / 1.5
    """
    b = inp.column_width_mm
    h = inp.column_depth_mm
    Ac = b * h  # Gross area (mm2)

    # Slenderness ratio
    lex = inp.height_m * 1000  # Assume effective length = height for braced
    ley = lex
    slenderness = max(lex / h, ley / b)
    is_short = slenderness <= 15

    if is_short:
        # Short braced column — simplified formula (BS 8110 Cl.3.8.4.3)
        # N = 0.4 * fck * Ac + 0.67 * Asc * fyk / 1.5
        # => Asc = (N - 0.4*fck*Ac) * 1.5 / (0.67 * fyk)

        N = inp.axial_load_kN * 1e3  # Convert to N

        Asc_required = (N - 0.4 * inp.fck * Ac) * 1.5 / (0.67 * inp.fyk)

        # Minimum reinforcement (BS 8110 Cl.3.12.5.2) — 0.4% of Ac
        Asc_min = 0.004 * Ac

        # Maximum reinforcement — 6% of Ac (BS 8110 Cl.3.12.5.1)
        Asc_max = 0.06 * Ac

        Asc_required = max(Asc_required, Asc_min)
        Asc_required = min(Asc_required, Asc_max)

        # If Asc_required is negative, column is oversized — provide minimum
        if Asc_required < 0:
            Asc_required = Asc_min

    else:
        # Slender column — simplified conservative approach
        # Use reduced capacity with additional moment
        N = inp.axial_load_kN * 1e3
        # Simplified: apply a reduction factor
        reduction = 1.0 - (slenderness - 15) * 0.01  # 1% reduction per unit above 15
        reduction = max(reduction, 0.6)

        Asc_required = (N / reduction - 0.4 * inp.fck * Ac) * 1.5 / (0.67 * inp.fyk)
        Asc_required = max(Asc_required, 0.004 * Ac)

    # Bar selection — even number for symmetry
    bar_dia = 16
    bar_area = math.pi * bar_dia**2 / 4
    n_bars = max(4, math.ceil(Asc_required / bar_area))
    if n_bars % 2 != 0:
        n_bars += 1  # Make even for symmetry

    Asc_provided = n_bars * bar_area

    # Ultimate capacity
    N_capacity = 0.4 * inp.fck * Ac + 0.67 * Asc_provided * inp.fyk / 1.5

    # Links
    link_dia = max(8, bar_dia / 4 * 2)  # At least quarter of main bar
    link_spacing = min(n_bars * 12, 300)  # Simplified

    return ColumnOutput(
        column_width_mm=b,
        column_depth_mm=h,
        slenderness_ratio=round(slenderness, 2),
        is_short=is_short,
        ultimate_capacity_kN=round(N_capacity / 1e3, 2),
        required_Asc_mm2=round(Asc_required, 1),
        provided_Asc_mm2=round(Asc_provided, 1),
        number_of_bars=n_bars,
        bar_diameter_mm=bar_dia,
        links_diameter_mm=round(link_dia),
        link_spacing_mm=round(link_spacing, 1),
        utilization_ratio=round(inp.axial_load_kN / (N_capacity / 1e3), 3),
        code_reference="BS 8110:1997, Part 1, Cl.3.8.4 (short braced), Cl.3.12.5 (reinforcement)",
    )
