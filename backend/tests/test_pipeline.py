"""
Tests for Site Assessment Pipeline
Validates the end-to-end pipeline from site data to design recommendations.
"""

import pytest
from app.pipeline.site_to_design import (
    SiteAssessmentInput,
    run_site_assessment_pipeline,
)


class TestPipeline:
    """Test the full site assessment → design pipeline."""

    def test_residential_dry_sand(self):
        """Typical residential project on dry sandy soil."""
        assessment = SiteAssessmentInput(
            project_name="Test Residential",
            project_id="test_001",
            engineer_name="Test Engineer",
            assessment_date="2025-01-15",
            terrain_type="flat",
            slope_angle_deg=0,
            groundwater_condition="none_observed",
            soil_color="yellowish brown",
            soil_texture="Sandy",
            soil_moisture="dry",
            pct_gravel=10,
            pct_sand=60,
            pct_silt=20,
            pct_clay=10,
            pct_organic=0,
            building_type="residential",
            number_of_stories=2,
            column_load_kN=400,
            total_building_load_kN=4000,
            footprint_area_m2=150,
            concrete_grade="C30",
        )

        result = run_site_assessment_pipeline(assessment)

        # Should classify as granular soil
        assert result.soil_classification.is_fine_grained is False
        assert result.recommended_bearing_capacity_kPa > 0
        assert result.foundation_recommendation.recommended is not None
        assert result.foundation_design is not None
        assert result.material_quantities.total_concrete_m3 > 0
        assert len(result.design_notes) > 0

    def test_commercial_soft_clay(self):
        """Commercial building on soft clay — should recommend piles."""
        assessment = SiteAssessmentInput(
            project_name="Test Commercial",
            project_id="test_002",
            engineer_name="Test Engineer",
            assessment_date="2025-01-15",
            terrain_type="flat",
            groundwater_condition="wet",
            water_table_depth_m=1.5,
            soil_color="dark grey",
            soil_texture="Clayey",
            soil_moisture="wet",
            pct_gravel=0,
            pct_sand=5,
            pct_silt=30,
            pct_clay=65,
            pct_organic=0,
            cohesion_kPa=30,
            building_type="commercial",
            number_of_stories=6,
            column_load_kN=2500,
            total_building_load_kN=25000,
            footprint_area_m2=500,
            concrete_grade="C35",
        )

        result = run_site_assessment_pipeline(assessment)

        # Should classify as fine-grained
        assert result.soil_classification.is_fine_grained is True
        # Should have groundwater warnings
        assert any("groundwater" in w.lower() or "water" in w.lower() for w in result.warnings)

    def test_organic_soil_pile_required(self):
        """Organic soil should always recommend pile foundation."""
        assessment = SiteAssessmentInput(
            project_name="Test Organic",
            project_id="test_003",
            engineer_name="Test Engineer",
            assessment_date="2025-01-15",
            pct_gravel=0,
            pct_sand=5,
            pct_silt=25,
            pct_clay=30,
            pct_organic=40,
            soil_color="dark brown",
            soil_texture="Organic",
            building_type="residential",
            number_of_stories=1,
            column_load_kN=150,
            total_building_load_kN=1000,
            footprint_area_m2=80,
        )

        result = run_site_assessment_pipeline(assessment)
        assert result.foundation_recommendation.recommended.value == "pile"

    def test_sloped_site_warning(self):
        """Sloped site should generate slope warning."""
        assessment = SiteAssessmentInput(
            project_name="Test Slope",
            project_id="test_004",
            engineer_name="Test Engineer",
            assessment_date="2025-01-15",
            terrain_type="moderate_slope",
            slope_angle_deg=20,
            pct_gravel=20,
            pct_sand=50,
            pct_silt=20,
            pct_clay=10,
            building_type="residential",
            number_of_stories=2,
            column_load_kN=400,
            total_building_load_kN=4000,
            footprint_area_m2=150,
        )

        result = run_site_assessment_pipeline(assessment)
        assert any("slope" in w.lower() for w in result.warnings)

    def test_estimated_parameters_generate_warnings(self):
        """When soil parameters are estimated, warnings should be generated."""
        assessment = SiteAssessmentInput(
            project_name="Test Estimates",
            project_id="test_005",
            engineer_name="Test Engineer",
            assessment_date="2025-01-15",
            pct_gravel=0,
            pct_sand=10,
            pct_silt=40,
            pct_clay=50,
            # NOT providing cohesion or phi — should estimate and warn
            building_type="residential",
            number_of_stories=2,
            column_load_kN=400,
            total_building_load_kN=4000,
            footprint_area_m2=150,
        )

        result = run_site_assessment_pipeline(assessment)
        assert any("estimated" in w.lower() or "testing recommended" in w.lower()
                    for w in result.warnings)
