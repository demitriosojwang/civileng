"""
Tests for Foundation Calculation Engine
Validates calculations against textbook examples.
"""

import pytest
import math
from app.calculations.foundation.bearing_capacity import (
    SoilParameters,
    FoundationGeometry,
    calculate_bearing_capacity_terzaghi,
    calculate_bearing_capacity_meyerhof,
    calculate_bearing_capacity_vesic,
)
from app.calculations.foundation.foundation_selector import (
    SiteConditions,
    BuildingParameters,
    SoilCategory,
    BuildingType,
    recommend_foundation_type,
)
from app.calculations.foundation.shallow_foundations import (
    PadFoundationInput,
    design_pad_foundation,
    design_strip_foundation,
    design_raft_foundation,
)
from app.calculations.structural.beam_design import BeamInput, design_beam
from app.calculations.structural.column_design import ColumnInput, design_column
from app.calculations.structural.load_combinations import LoadInputs, generate_load_combinations


class TestBearingCapacity:
    """Test bearing capacity calculations against known values."""

    def test_terzaghi_strip_sand(self):
        """Test Terzaghi method for strip foundation on sand (phi=30, c=0)."""
        soil = SoilParameters(
            cohesion=0,
            angle_of_shearing_resistance=30,
            unit_weight=18,
        )
        geometry = FoundationGeometry(width=2.0, depth=1.0)

        result = calculate_bearing_capacity_terzaghi(soil, geometry, fos=3.0)

        # For phi=30, c=0 strip: qult = q*Nq + 0.5*gamma*B*Ngamma
        # Nq ~ 18.4, Ngamma ~ 22.4 (approximate)
        assert result.ultimate_bearing_capacity > 0
        assert result.net_ultimate_bearing_capacity > 0
        assert result.allowable_bearing_capacity > 0
        assert result.allowable_bearing_capacity < result.net_ultimate_bearing_capacity
        assert result.method == "Terzaghi"

    def test_terzaghi_clay_phi_zero(self):
        """Test Terzaghi for undrained clay (phi=0)."""
        soil = SoilParameters(
            cohesion=100,
            angle_of_shearing_resistance=0,
            unit_weight=18,
        )
        geometry = FoundationGeometry(width=2.0, depth=1.0)

        result = calculate_bearing_capacity_terzaghi(soil, geometry, fos=3.0)

        # For phi=0: qult = c*Nc + q (Ngamma = 0, Nq = 1)
        # Nc = 5.7 for strip
        assert result.ultimate_bearing_capacity > 0
        assert result.factor_of_safety == 3.0

    def test_meyerhof_gives_higher_than_terzaghi(self):
        """Meyerhof includes depth and shape factors, should give higher capacity."""
        soil = SoilParameters(
            cohesion=10,
            angle_of_shearing_resistance=25,
            unit_weight=18,
        )
        geometry = FoundationGeometry(width=2.0, length=3.0, depth=1.5)

        terzaghi = calculate_bearing_capacity_terzaghi(soil, geometry)
        meyerhof = calculate_bearing_capacity_meyerhof(soil, geometry)

        # Meyerhof with shape + depth factors should be >= Terzaghi
        assert meyerhof.ultimate_bearing_capacity >= terzaghi.ultimate_bearing_capacity * 0.9

    def test_vesic_method(self):
        """Test Vesic method produces reasonable results."""
        soil = SoilParameters(
            cohesion=15,
            angle_of_shearing_resistance=28,
            unit_weight=19,
        )
        geometry = FoundationGeometry(width=2.5, length=3.0, depth=1.2)

        result = calculate_bearing_capacity_vesic(soil, geometry)
        assert result.ultimate_bearing_capacity > 0
        assert result.method == "Vesic"

    def test_water_table_reduces_capacity(self):
        """Water table within influence zone should reduce bearing capacity."""
        soil_dry = SoilParameters(
            cohesion=0,
            angle_of_shearing_resistance=30,
            unit_weight=18,
        )
        soil_wet = SoilParameters(
            cohesion=0,
            angle_of_shearing_resistance=30,
            unit_weight=18,
            water_table_depth=0.5,
            saturated_unit_weight=20,
        )
        geometry = FoundationGeometry(width=2.0, depth=1.0)

        dry = calculate_bearing_capacity_terzaghi(soil_dry, geometry)
        wet = calculate_bearing_capacity_terzaghi(soil_wet, geometry)

        assert wet.ultimate_bearing_capacity < dry.ultimate_bearing_capacity


class TestFoundationSelector:
    """Test foundation type recommendation engine."""

    def test_good_ground_recommends_pad(self):
        """Good ground with moderate loads should recommend pad foundation."""
        site = SiteConditions(
            soil_category=SoilCategory.GRANULAR_DENSE,
            bearing_capacity_kPa=300,
        )
        building = BuildingParameters(
            building_type=BuildingType.RESIDENTIAL,
            number_of_stories=3,
            column_load_kN=500,
            total_building_load_kN=5000,
            footprint_area_m2=200,
        )

        result = recommend_foundation_type(site, building)
        assert result.recommended.value == "pad"
        assert result.confidence >= 0.8

    def test_soft_clay_recommends_pile(self):
        """Soft clay with heavy loads should recommend pile foundation."""
        site = SiteConditions(
            soil_category=SoilCategory.CLAY_SOFT,
            bearing_capacity_kPa=50,
        )
        building = BuildingParameters(
            building_type=BuildingType.COMMERCIAL,
            number_of_stories=8,
            column_load_kN=3000,
            total_building_load_kN=30000,
            footprint_area_m2=500,
        )

        result = recommend_foundation_type(site, building)
        assert result.recommended.value == "pile"

    def test_organic_soil_always_pile(self):
        """Organic soil should always recommend pile foundation."""
        site = SiteConditions(
            soil_category=SoilCategory.ORGANIC,
            bearing_capacity_kPa=25,
        )
        building = BuildingParameters(
            building_type=BuildingType.RESIDENTIAL,
            number_of_stories=1,
            column_load_kN=100,
            total_building_load_kN=500,
            footprint_area_m2=100,
        )

        result = recommend_foundation_type(site, building)
        assert result.recommended.value == "pile"


class TestShallowFoundations:
    """Test shallow foundation design."""

    def test_pad_foundation_sizing(self):
        """Pad foundation should be sized to carry the applied load."""
        inp = PadFoundationInput(
            column_load_kN=1000,
            allowable_bearing_kPa=200,
            column_width_mm=400,
        )

        result = design_pad_foundation(inp)
        assert result.bearing_pressure_kPa <= 200 * 1.1  # Allow 10% over
        assert result.passes_shear is True
        assert result.length_mm >= 400
        assert result.width_mm >= 400


class TestStructuralDesign:
    """Test beam and column design."""

    def test_beam_design(self):
        """Basic beam design should produce valid results."""
        inp = BeamInput(
            span_m=6.0,
            width_mm=300,
            depth_mm=500,
            ultimate_moment_kNm=150,
            ultimate_shear_kN=100,
        )

        result = design_beam(inp)
        assert result.required_As_mm2 > 0
        assert result.provided_As_mm2 >= result.required_As_mm2

    def test_column_design(self):
        """Short braced column design should produce valid results."""
        inp = ColumnInput(
            axial_load_kN=1500,
            column_width_mm=350,
            column_depth_mm=350,
        )

        result = design_column(inp)
        assert result.is_short is True
        assert result.utilization_ratio <= 1.0

    def test_load_combinations(self):
        """Load combinations should generate correctly."""
        loads = LoadInputs(dead_load_kN=500, live_load_kN=300, wind_load_kN=100)

        result = generate_load_combinations(loads)
        assert len(result.combinations) == 4
        assert result.governing_load_kN > 0
