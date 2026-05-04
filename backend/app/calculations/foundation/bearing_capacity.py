"""
Bearing Capacity Calculations
Implements Terzaghi, Meyerhof, and Vesic methods for shallow foundation bearing capacity.

References:
- BS 8004:2015 — Code of practice for foundations
- EN 1997-1:2004 — Eurocode 7: Geotechnical design
- Craig's Soil Mechanics (8th ed.)
"""

import math
from typing import Optional
from pydantic import BaseModel, Field


class SoilParameters(BaseModel):
    """Input soil parameters for bearing capacity calculation."""
    cohesion: float = Field(..., description="Undrained cohesion cu (kPa)")
    angle_of_shearing_resistance: float = Field(..., description="Effective angle of shearing resistance phi' (degrees)")
    unit_weight: float = Field(..., description="Soil unit weight gamma (kN/m3)")
    water_table_depth: Optional[float] = Field(None, description="Depth to water table from ground level (m)")
    saturated_unit_weight: Optional[float] = Field(None, description="Saturated unit weight gamma_sat (kN/m3)")


class FoundationGeometry(BaseModel):
    """Foundation dimensions and embedment."""
    width: float = Field(..., gt=0, description="Foundation width B (m)")
    length: Optional[float] = Field(None, gt=0, description="Foundation length L (m) — None for strip/continuous")
    depth: float = Field(..., ge=0, description="Depth of embedment D (m)")


class BearingCapacityResult(BaseModel):
    """Output from bearing capacity calculation."""
    method: str
    ultimate_bearing_capacity: float = Field(..., description="qult (kPa)")
    net_ultimate_bearing_capacity: float = Field(..., description="qnet (kPa)")
    allowable_bearing_capacity: float = Field(..., description="qall (kPa) with factor of safety applied")
    factor_of_safety: float
    code_reference: str
    intermediate_steps: dict


# --- Terzaghi Bearing Capacity Factors ---

def _terzaghi_Nc(phi_deg: float) -> float:
    """Terzaghi bearing capacity factor Nc."""
    if phi_deg <= 0:
        return 5.7  # For phi=0 (undrained clay)
    phi_rad = math.radians(phi_deg)
    return (math.cos(phi_rad) / math.cos(phi_rad - 0.0)) * \
           ((math.exp(math.pi * math.tan(phi_rad))) / (2 * math.cos(phi_rad)**2)) * \
           (1 / (1 - math.sin(phi_rad))) if phi_deg > 0 else 5.7


def _terzaghi_Nq(phi_deg: float) -> float:
    """Terzaghi bearing capacity factor Nq."""
    if phi_deg <= 0:
        return 1.0
    phi_rad = math.radians(phi_deg)
    return (math.exp(2 * math.pi * math.tan(phi_rad) * 0.5)) * \
           (1 / (1 - math.sin(phi_rad))) * (1 + math.sin(phi_rad)) / 2


def _terzaghi_Ngamma(phi_deg: float) -> float:
    """Terzaghi bearing capacity factor Ngamma (approximate)."""
    if phi_deg <= 0:
        return 0.0
    phi_rad = math.radians(phi_deg)
    return 1.8 * (math.exp(math.pi * math.tan(phi_rad)) - 1) * math.tan(phi_rad) * 0.5


def _terzaghi_shape_factors(foundation_type: str, Nq: float):
    """Terzaghi shape factors for strip, square, and circular foundations."""
    if foundation_type == "strip":
        return 1.0, 1.0, 1.0  # sc, sq, sgamma
    elif foundation_type == "square":
        return 1.3, 1.0, 0.8
    elif foundation_type == "circular":
        return 1.3, 1.0, 0.6
    elif foundation_type == "rectangular":
        return 1.0 + 0.3, 1.0, 1.0 - 0.2  # Simplified; actual depends on B/L ratio
    else:
        return 1.0, 1.0, 1.0


def calculate_bearing_capacity_terzaghi(
    soil: SoilParameters,
    geometry: FoundationGeometry,
    factor_of_safety: float = 3.0,
    foundation_type: str = "strip",
) -> BearingCapacityResult:
    """
    Calculate bearing capacity using Terzaghi's method.

    qult = c*Nc*sc + q*Nq*sq + 0.5*gamma*B*Ngamma*sgamma

    Where:
    - c = cohesion (kPa)
    - q = gamma * D (surcharge from embedment)
    - gamma = soil unit weight below foundation
    - B = foundation width
    - Nc, Nq, Ngamma = bearing capacity factors
    - sc, sq, sgamma = shape factors
    """
    phi = soil.angle_of_shearing_resistance
    c = soil.cohesion
    gamma = soil.unit_weight
    B = geometry.width
    D = geometry.depth

    # Bearing capacity factors
    Nc = _terzaghi_Nc(phi)
    Nq = _terzaghi_Nq(phi)
    Ngamma = _terzaghi_Ngamma(phi)

    # Shape factors
    sc, sq, sgamma = _terzaghi_shape_factors(foundation_type, Nq)

    # Surcharge
    q = gamma * D

    # Adjust unit weight if water table is within influence zone
    gamma_eff = gamma
    if soil.water_table_depth is not None and soil.water_table_depth < D + B:
        # Water table within influence zone — use submerged unit weight
        if soil.saturated_unit_weight:
            gamma_sub = soil.saturated_unit_weight - 9.81  # gamma_sub = gamma_sat - gamma_w
        else:
            gamma_sub = gamma - 9.81
        gamma_eff = gamma_sub

    # Ultimate bearing capacity
    qult = (c * Nc * sc) + (q * Nq * sq) + (0.5 * gamma_eff * B * Ngamma * sgamma)

    # Net ultimate bearing capacity
    q_net = qult - q

    # Allowable bearing capacity
    q_all = q_net / factor_of_safety

    return BearingCapacityResult(
        method="Terzaghi",
        ultimate_bearing_capacity=round(qult, 2),
        net_ultimate_bearing_capacity=round(q_net, 2),
        allowable_bearing_capacity=round(q_all, 2),
        factor_of_safety=factor_of_safety,
        code_reference="BS 8004:2015, Section 5.2 / Craig's Soil Mechanics Ch.8",
        intermediate_steps={
            "Nc": round(Nc, 4),
            "Nq": round(Nq, 4),
            "Ngamma": round(Ngamma, 4),
            "sc": round(sc, 4),
            "sq": round(sq, 4),
            "sgamma": round(sgamma, 4),
            "surcharge_q": round(q, 2),
            "effective_unit_weight": round(gamma_eff, 2),
        }
    )


# --- Meyerhof Bearing Capacity ---

def _meyerhof_factors(phi_deg: float):
    """Meyerhof bearing capacity factors with general shape and depth factors."""
    phi_rad = math.radians(phi_deg)

    Nq = math.exp(math.pi * math.tan(phi_rad)) * (1 + math.sin(phi_rad)) / (1 - math.sin(phi_rad))
    Nc = (Nq - 1) / math.tan(phi_rad) if phi_deg > 0 else 5.14
    Ngamma = (Nq - 1) * math.tan(1.4 * phi_rad)

    return Nc, Nq, Ngamma


def calculate_bearing_capacity_meyerhof(
    soil: SoilParameters,
    geometry: FoundationGeometry,
    factor_of_safety: float = 3.0,
) -> BearingCapacityResult:
    """
    Calculate bearing capacity using Meyerhof's method (general equation).

    qult = c*Nc*sc*dc + q*Nq*sq*dq + 0.5*gamma*B*Ngamma*sgamma*dgamma

    Includes shape and depth factors.
    Reference: Meyerhof (1963), BS 8004:2015
    """
    phi = soil.angle_of_shearing_resistance
    c = soil.cohesion
    gamma = soil.unit_weight
    B = geometry.width
    L = geometry.length or B  # Default to square if not specified
    D = geometry.depth

    Nc, Nq, Ngamma = _meyerhof_factors(phi)

    # Shape factors (Meyerhof)
    sc = 1 + 0.2 * (B / L) * math.tan(math.radians(45 + phi / 2)) if phi > 0 else 1.0
    sq = 1 + 0.1 * (B / L) * Nq if phi > 0 else 1.0
    sgamma = sq  # Same as sq for Meyerhof

    # Depth factors (Meyerhof)
    dc = 1 + 0.2 * math.sqrt(D / B) * math.tan(math.radians(45 + phi / 2)) if phi > 0 else 1.0
    dq = 1 + 0.1 * math.sqrt(D / B) * Nq if phi > 0 else 1.0
    dgamma = dq

    # Surcharge
    q = gamma * D

    # Adjust for water table
    gamma_eff = gamma
    if soil.water_table_depth is not None and soil.water_table_depth < D + B:
        gamma_eff = (soil.saturated_unit_weight or gamma) - 9.81

    # Ultimate bearing capacity
    qult = (c * Nc * sc * dc) + (q * Nq * sq * dq) + (0.5 * gamma_eff * B * Ngamma * sgamma * dgamma)

    q_net = qult - q
    q_all = q_net / factor_of_safety

    return BearingCapacityResult(
        method="Meyerhof",
        ultimate_bearing_capacity=round(qult, 2),
        net_ultimate_bearing_capacity=round(q_net, 2),
        allowable_bearing_capacity=round(q_all, 2),
        factor_of_safety=factor_of_safety,
        code_reference="Meyerhof (1963) / BS 8004:2015 / EN 1997-1 Annex D",
        intermediate_steps={
            "Nc": round(Nc, 4),
            "Nq": round(Nq, 4),
            "Ngamma": round(Ngamma, 4),
            "sc": round(sc, 4),
            "sq": round(sq, 4),
            "sgamma": round(sgamma, 4),
            "dc": round(dc, 4),
            "dq": round(dq, 4),
            "dgamma": round(dgamma, 4),
            "surcharge_q": round(q, 2),
            "effective_unit_weight": round(gamma_eff, 2),
        }
    )


# --- Vesic Bearing Capacity ---

def calculate_bearing_capacity_vesic(
    soil: SoilParameters,
    geometry: FoundationGeometry,
    factor_of_safety: float = 3.0,
) -> BearingCapacityResult:
    """
    Calculate bearing capacity using Vesic's method.

    Same general form as Meyerhof but with different factor expressions.
    Reference: Vesic (1973, 1975)
    """
    phi = soil.angle_of_shearing_resistance
    c = soil.cohesion
    gamma = soil.unit_weight
    B = geometry.width
    L = geometry.length or B
    D = geometry.depth

    phi_rad = math.radians(phi)

    # Vesic factors (same Nq as Meyerhof)
    Nq = math.exp(math.pi * math.tan(phi_rad)) * (1 + math.sin(phi_rad)) / (1 - math.sin(phi_rad))
    Nc = (Nq - 1) / math.tan(phi_rad) if phi > 0 else 5.14
    Ngamma = 2 * (Nq + 1) * math.tan(phi_rad)  # Vesic's Ngamma

    # Shape factors (Vesic)
    sc = 1 + (B / L) * (Nq / Nc) if phi > 0 else 1.0
    sq = 1 + (B / L) * math.tan(phi_rad)
    sgamma = 1 - 0.4 * (B / L)

    # Depth factors (Vesic)
    k = min(D / B, 1.0)
    dc = 1 + 0.4 * k if phi == 0 else 1 + 0.4 * k * math.tan(math.radians(45 + phi / 2))
    dq = 1 + 2 * math.tan(phi_rad) * (1 - math.sin(phi_rad))**2 * k
    dgamma = 1.0  # Vesic takes dgamma = 1

    q = gamma * D

    gamma_eff = gamma
    if soil.water_table_depth is not None and soil.water_table_depth < D + B:
        gamma_eff = (soil.saturated_unit_weight or gamma) - 9.81

    qult = (c * Nc * sc * dc) + (q * Nq * sq * dq) + (0.5 * gamma_eff * B * Ngamma * sgamma * dgamma)

    q_net = qult - q
    q_all = q_net / factor_of_safety

    return BearingCapacityResult(
        method="Vesic",
        ultimate_bearing_capacity=round(qult, 2),
        net_ultimate_bearing_capacity=round(q_net, 2),
        allowable_bearing_capacity=round(q_all, 2),
        factor_of_safety=factor_of_safety,
        code_reference="Vesic (1973) / EN 1997-1 Annex D",
        intermediate_steps={
            "Nc": round(Nc, 4),
            "Nq": round(Nq, 4),
            "Ngamma": round(Ngamma, 4),
            "sc": round(sc, 4),
            "sq": round(sq, 4),
            "sgamma": round(sgamma, 4),
            "dc": round(dc, 4),
            "dq": round(dq, 4),
            "dgamma": round(dgamma, 4),
            "surcharge_q": round(q, 2),
            "effective_unit_weight": round(gamma_eff, 2),
        }
    )
