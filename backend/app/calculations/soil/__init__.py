"""
Soil Classification Module
Implements soil classification per BS 5930 and ISO 14688.
"""

from .classifier import classify_soil, SoilClassificationInput, SoilClassificationResult

__all__ = ["classify_soil", "SoilClassificationInput", "SoilClassificationResult"]
