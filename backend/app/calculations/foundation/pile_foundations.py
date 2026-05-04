"""
Pile Foundation Design Calculations
Implements pile capacity calculations per BS 8004.

References:
- BS 8004:2015 Section 7 — Pile foundations
- Tomlinson's Pile Design & Construction Practice
"""

import math
from pydantic import BaseModel, Field
from typing import List, Optional


class PileSoilLayer(BaseModel):
    """A soil layer along the pile shaft."""
    top_depth_m: float = Field(..., ge=0)
    bottom_depth_m: float = Field(..., gt=0)
    soil_type: str = Field(..., description="clay / sand / rock")
    cohesion_kPa: Optional[float] = Field(None, description="Undrained cohesion for clay (kPa)")
    angle_of_shearing_resistance_deg: Optional[float] = Field(None, description="Phi' for sand (degrees)")
    unit_weight_kN_m3: float = Field(18, description="Unit weight (kN/m3)")
    SPT_N: Optional[int] = Field(None, description="SPT N-value for granular soils")


class PileInput(BaseModel):
    """Input parameters for pile capacity calculation."""
    pile_diameter_m: float = Field(..., gt=0, description="Pile diameter (m)")
    pile_length_m: float = Field(..., gt=0, description="Pile length from cut-off to toe (m)")
    soil_layers: List[PileSoilLayer] = Field(..., min_length=1)
    water_table_depth_m: Optional[float] = Field(None)
    end_bearing_stratum: str = Field(..., description="clay / sand / rock")
    end_bearing_N_value: Optional[int] = Field(None, description="SPT N at pile toe level")
    end_bearing_cohesion_kPa: Optional[float] = Field(None, description="cu at pile toe (kPa)")


class PileCapacityResult(BaseModel):
    """Pile capacity calculation result."""
    shaft_friction_kN: float
    end_bearing_kN: float
    total_ultimate_capacity_kN: float
    allowable_capacity_kN: float
    factor_of_safety: float
    shaft_friction_details: list
    end_bearing_details: dict
    code_reference: str


def design_pile_foundation(inp: PileInput, fos: float = 2.5) -> PileCapacityResult:
    """
    Calculate pile capacity using alpha-method (clay) and beta-method (sand) for shaft friction,
    and appropriate end-bearing formulas.

    BS 8004 Section 7:
    - Clay shaft: Qs = alpha * cu * As
    - Sand shaft: Qs = K * sigma_v' * tan(delta) * As (or from SPT correlations)
    - End bearing clay: Qb = Nc * cu * Ab (Nc = 9)
    - End bearing sand: Qb = Nq * sigma_v' * Ab
    """
    D = inp.pile_diameter_m
    L = inp.pile_length_m
    perimeter = math.pi * D
    base_area = math.pi * D**2 / 4

    shaft_friction_total = 0.0
    shaft_details = []

    for i, layer in enumerate(inp.soil_layers):
        layer_thickness = layer.bottom_depth_m - layer.top_depth_m
        shaft_area = perimeter * layer_thickness  # m2

        # Effective vertical stress at layer mid-point
        sigma_v = layer.unit_weight_kN_m3 * (layer.top_depth_m + layer.bottom_depth_m) / 2

        # Adjust for water table
        if inp.water_table_depth_m is not None and layer.top_depth_m > inp.water_table_depth_m:
            sigma_v_eff = sigma_v - 9.81 * (layer.bottom_depth_m - max(layer.top_depth_m, inp.water_table_depth_m)) / 2
        else:
            sigma_v_eff = sigma_v

        if layer.soil_type == "clay" and layer.cohesion_kPa is not None:
            # Alpha method: alpha * cu * As
            alpha = 0.5  # Simplified — BS 8004 suggests 0.3-0.6 depending on cu
            if layer.cohesion_kPa > 150:
                alpha = 0.3
            elif layer.cohesion_kPa > 75:
                alpha = 0.4
            else:
                alpha = 0.5

            qs = alpha * layer.cohesion_kPa * shaft_area  # kN
            shaft_details.append({
                "layer": i + 1,
                "type": "clay",
                "alpha": alpha,
                "cu_kPa": layer.cohesion_kPa,
                "shaft_area_m2": round(shaft_area, 2),
                "shaft_friction_kN": round(qs, 2),
            })

        elif layer.soil_type == "sand":
            # Beta method: K * sigma_v' * tan(delta) * As
            # For driven piles K = 1-2, for bored K = 0.5-1.0
            K = 0.7  # Conservative for bored piles
            delta = 0.67 * (layer.angle_of_shearing_resistance_deg or 30)  # degrees

            qs = K * sigma_v_eff * math.tan(math.radians(delta)) * shaft_area  # kN

            # Alternative: SPT correlation (Meyerhof)
            if layer.SPT_N is not None:
                qs_spt = layer.SPT_N * shaft_area / 50  # kN (simplified Meyerhof)
                qs = min(qs, qs_spt)  # Take conservative

            shaft_details.append({
                "layer": i + 1,
                "type": "sand",
                "K": K,
                "delta_deg": round(delta, 1),
                "sigma_v_eff_kPa": round(sigma_v_eff, 2),
                "shaft_area_m2": round(shaft_area, 2),
                "shaft_friction_kN": round(qs, 2),
            })
        else:
            # Rock — very high shaft friction, limited by concrete-rock interface
            qs = 200 * shaft_area  # 200 kPa conservative rock shaft adhesion
            shaft_details.append({
                "layer": i + 1,
                "type": "rock",
                "shaft_area_m2": round(shaft_area, 2),
                "shaft_friction_kN": round(qs, 2),
            })

        shaft_friction_total += qs

    # End bearing calculation
    if inp.end_bearing_stratum == "clay" and inp.end_bearing_cohesion_kPa is not None:
        Nc = 9.0  # For deep foundations in clay
        Qb = Nc * inp.end_bearing_cohesion_kPa * base_area  # kN
        end_bearing_details = {
            "method": "Nc * cu * Ab",
            "Nc": Nc,
            "cu_kPa": inp.end_bearing_cohesion_kPa,
            "base_area_m2": round(base_area, 4),
            "end_bearing_kN": round(Qb, 2),
        }

    elif inp.end_bearing_stratum == "sand" and inp.end_bearing_N_value is not None:
        # Meyerhof end bearing from SPT
        Qb = inp.end_bearing_N_value * 40 * base_area / 1000 * 1000  # Simplified
        # More accurately: qb = 40 * N * D/B (kPa), limited to max
        qb = min(40 * inp.end_bearing_N_value, 10000)  # kPa, capped at 10 MPa
        Qb = qb * base_area  # kN

        end_bearing_details = {
            "method": "Meyerhof SPT correlation",
            "SPT_N": inp.end_bearing_N_value,
            "qb_kPa": round(qb, 2),
            "base_area_m2": round(base_area, 4),
            "end_bearing_kN": round(Qb, 2),
        }
    else:
        # Rock end bearing
        qb = 10000  # 10 MPa conservative for rock
        Qb = qb * base_area
        end_bearing_details = {
            "method": "Rock end bearing (conservative)",
            "qb_kPa": qb,
            "base_area_m2": round(base_area, 4),
            "end_bearing_kN": round(Qb, 2),
        }

    total_ultimate = shaft_friction_total + Qb
    allowable = total_ultimate / fos

    return PileCapacityResult(
        shaft_friction_kN=round(shaft_friction_total, 2),
        end_bearing_kN=round(Qb, 2),
        total_ultimate_capacity_kN=round(total_ultimate, 2),
        allowable_capacity_kN=round(allowable, 2),
        factor_of_safety=fos,
        shaft_friction_details=shaft_details,
        end_bearing_details=end_bearing_details,
        code_reference="BS 8004:2015 Section 7 / Tomlinson's Pile Design",
    )
