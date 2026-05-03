"""
Structural Design Calculations Module
Beam, column, and slab design per BS 8110 and Eurocode 2.
"""

from .beam_design import design_beam
from .column_design import design_column
from .load_combinations import generate_load_combinations

__all__ = [
    "design_beam",
    "design_column",
    "generate_load_combinations",
]
