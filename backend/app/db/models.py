"""
Database Models for CivilEng
SQLAlchemy ORM models for projects, site assessments, and design results.
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, Date,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Project(Base):
    """Construction project."""
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, default="")
    client_name = Column(String(255), default="")
    location = Column(String(500), default="")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String(50), default="active")  # active, completed, archived
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assessments = relationship("SiteAssessment", back_populates="project", cascade="all, delete-orphan")


class SiteAssessment(Base):
    """Site assessment data captured from mobile app."""
    __tablename__ = "site_assessments"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    engineer_name = Column(String(255), default="")
    assessment_date = Column(Date, default=None)

    # Terrain
    terrain_type = Column(String(50), default="flat")
    slope_angle_deg = Column(Float, default=0)
    slope_direction = Column(String(100), default="")

    # Groundwater
    groundwater_condition = Column(String(50), default="none_observed")
    water_table_depth_m = Column(Float, nullable=True)
    drainage_description = Column(Text, default="")

    # Soil visual
    soil_color = Column(String(100), default="")
    soil_texture = Column(String(100), default="")
    soil_moisture = Column(String(50), default="dry")
    soil_layering_observed = Column(Boolean, default=False)
    soil_layer_description = Column(Text, default="")
    rock_outcrops = Column(Boolean, default=False)
    rock_type = Column(String(100), default="")

    # Soil parameters
    cohesion_kPa = Column(Float, nullable=True)
    angle_of_shearing_resistance_deg = Column(Float, nullable=True)
    unit_weight_kN_m3 = Column(Float, nullable=True)
    liquid_limit_pct = Column(Float, nullable=True)
    plastic_limit_pct = Column(Float, nullable=True)
    spt_n_values = Column(JSON, default=list)

    # Particle size distribution
    pct_gravel = Column(Float, default=0)
    pct_sand = Column(Float, default=0)
    pct_silt = Column(Float, default=0)
    pct_clay = Column(Float, default=0)
    pct_organic = Column(Float, default=0)

    # Environmental flags
    expansive_soil = Column(Boolean, default=False)
    seismic_zone = Column(Boolean, default=False)

    # Adjacent structures
    adjacent_structures = Column(Boolean, default=False)
    adjacent_condition = Column(String(100), default="none")
    adjacent_description = Column(Text, default="")

    # Access
    access_road_type = Column(String(100), default="")
    site_access_notes = Column(Text, default="")

    # Photo references
    photo_ids = Column(JSON, default=list)

    # Sync status
    synced = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="assessments")
    designs = relationship("DesignResult", back_populates="assessment", cascade="all, delete-orphan")


class DesignResult(Base):
    """Design calculation results from the pipeline."""
    __tablename__ = "design_results"

    id = Column(String, primary_key=True)
    assessment_id = Column(String, ForeignKey("site_assessments.id"), nullable=False)

    # Pipeline outputs stored as JSON
    soil_classification = Column(JSON, default=dict)
    bearing_capacity = Column(JSON, default=dict)
    foundation_recommendation = Column(JSON, default=dict)
    foundation_design = Column(JSON, default=dict)
    material_quantities = Column(JSON, default=dict)
    warnings = Column(JSON, default=list)
    design_notes = Column(JSON, default=list)

    # Summary fields for quick queries
    recommended_bearing_capacity_kPa = Column(Float, default=0)
    recommended_foundation_type = Column(String(50), default="")
    confidence_score = Column(Float, default=0)
    total_concrete_m3 = Column(Float, default=0)
    total_rebar_kg = Column(Float, default=0)

    # Report
    report_pdf_path = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    assessment = relationship("SiteAssessment", back_populates="designs")


class Photo(Base):
    """Site photo metadata."""
    __tablename__ = "photos"

    id = Column(String, primary_key=True)
    assessment_id = Column(String, ForeignKey("site_assessments.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    caption = Column(Text, default="")
    angle = Column(String(100), default="")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
