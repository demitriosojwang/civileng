"""
Foundation Design Calculations Module
Implements bearing capacity and foundation sizing per BS 8004 and Eurocode 7.
"""

from .bearing_capacity import (
    calculate_bearing_capacity_terzaghi,
    calculate_bearing_capacity_meyerhof,
    calculate_bearing_capacity_vesic,
)
from .foundation_selector import recommend_foundation_type
from .shallow_foundations import design_pad_foundation, design_strip_foundation, design_raft_foundation
from .pile_foundations import design_pile_foundation

__all__ = [
    "calculate_bearing_capacity_terzaghi",
    "calculate_bearing_capacity_meyerhof",
    "calculate_bearing_capacity_vesic",
    "recommend_foundation_type",
    "design_pad_foundation",
    "design_strip_foundation",
    "design_raft_foundation",
    "design_pile_foundation",
]
