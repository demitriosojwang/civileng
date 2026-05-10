"""
Load Combination Generator
Generates load combinations per BS 6399 and EN 1990.
"""

from pydantic import BaseModel, Field
from typing import List


class LoadInputs(BaseModel):
    dead_load_kN: float = Field(..., ge=0, description="Characteristic dead load (kN)")
    live_load_kN: float = Field(..., ge=0, description="Characteristic imposed/live load (kN)")
    wind_load_kN: float = Field(0, ge=0, description="Characteristic wind load (kN)")


class LoadCombination(BaseModel):
    name: str
    code: str
    factors: dict
    total_kN: float


class LoadCombinationResult(BaseModel):
    combinations: List[LoadCombination]
    governing_combination: str
    governing_load_kN: float


def generate_load_combinations(loads: LoadInputs) -> LoadCombinationResult:
    """
    Generate load combinations per BS 6399 / EN 1990.

    BS 6399 / EN 1990 combinations:
    1. 1.35Gk + 1.50Qk (dead + live, no wind)
    2. 1.35Gk + 1.50Qk + 0.75Wk (dead + live + reduced wind)
    3. 1.35Gk + 1.50Wk + 0.75Qk (dead + wind + reduced live)
    4. 1.00Gk + 1.50Wk (dead only + wind, for stability)
    """
    G = loads.dead_load_kN
    Q = loads.live_load_kN
    W = loads.wind_load_kN

    combinations = [
        LoadCombination(
            name="Combination 1: Dead + Live",
            code="EN 1990 Eq.6.10(b)",
            factors={"gamma_G": 1.35, "gamma_Q": 1.50, "gamma_W": 0},
            total_kN=round(1.35 * G + 1.50 * Q, 2),
        ),
        LoadCombination(
            name="Combination 2: Dead + Live + Wind",
            code="EN 1990 Eq.6.10(b) + wind",
            factors={"gamma_G": 1.35, "gamma_Q": 1.50, "gamma_W": 0.75},
            total_kN=round(1.35 * G + 1.50 * Q + 0.75 * W, 2),
        ),
        LoadCombination(
            name="Combination 3: Dead + Wind + Reduced Live",
            code="EN 1990 Eq.6.10(b) alt.",
            factors={"gamma_G": 1.35, "gamma_Q": 0.75, "gamma_W": 1.50},
            total_kN=round(1.35 * G + 0.75 * Q + 1.50 * W, 2),
        ),
        LoadCombination(
            name="Combination 4: Dead + Wind (stability)",
            code="EN 1990 Eq.6.10(a)",
            factors={"gamma_G": 1.00, "gamma_Q": 0, "gamma_W": 1.50},
            total_kN=round(1.00 * G + 1.50 * W, 2),
        ),
    ]

    # Find governing combination
    governing = max(combinations, key=lambda c: c.total_kN)

    return LoadCombinationResult(
        combinations=combinations,
        governing_combination=governing.name,
        governing_load_kN=governing.total_kN,
    )
