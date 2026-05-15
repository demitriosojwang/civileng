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


# ─── Admin Moderation Models ───


class AdminUser(Base):
    """Internal team member with admin/moderation access."""
    __tablename__ = "admin_users"

    id = Column(String, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    display_name = Column(String(255), default="")
    role = Column(String(50), default="moderator")  # super_admin, admin, moderator, viewer
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    review_actions = relationship("ReviewAction", back_populates="admin", cascade="all, delete-orphan")
    dispute_assignments = relationship("Dispute", foreign_keys="Dispute.assigned_to", back_populates="assignee")


class Review(Base):
    """Design/calculation review submitted for approval."""
    __tablename__ = "reviews"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    design_id = Column(String, ForeignKey("design_results.id"), nullable=True)

    # Who submitted the review request
    submitted_by = Column(String(255), nullable=False)  # engineer name or user ID
    submitted_by_email = Column(String(255), default="")

    # Review content
    title = Column(String(500), default="")
    description = Column(Text, default="")
    review_type = Column(String(50), default="design_approval")  # design_approval, calculation_check, report_review
    priority = Column(String(20), default="normal")  # urgent, high, normal, low

    # Design summary for quick review
    foundation_type = Column(String(50), default="")
    bearing_capacity_kPa = Column(Float, nullable=True)
    total_concrete_m3 = Column(Float, nullable=True)
    total_rebar_kg = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)

    # Code compliance
    standards_used = Column(JSON, default=list)  # ["BS 8004", "BS 8110"]
    compliance_notes = Column(Text, default="")
    has_warnings = Column(Boolean, default=False)
    warning_count = Column(Integer, default=0)

    # Status workflow
    status = Column(String(30), default="pending")  # pending, in_review, approved, rejected, revisions_needed
    assigned_reviewer = Column(String(255), nullable=True)

    # Attachments
    attachment_ids = Column(JSON, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    actions = relationship("ReviewAction", back_populates="review", cascade="all, delete-orphan")


class ReviewAction(Base):
    """Audit trail of actions taken on a review."""
    __tablename__ = "review_actions"

    id = Column(String, primary_key=True)
    review_id = Column(String, ForeignKey("reviews.id"), nullable=False)
    admin_id = Column(String, ForeignKey("admin_users.id"), nullable=False)

    action = Column(String(50), nullable=False)  # approved, rejected, requested_revision, commented, escalated, assigned
    comment = Column(Text, default="")
    old_status = Column(String(30), default="")
    new_status = Column(String(30), default="")

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    review = relationship("Review", back_populates="actions")
    admin = relationship("AdminUser", back_populates="review_actions")


class Dispute(Base):
    """Dispute raised by a party regarding a design or tender."""
    __tablename__ = "disputes"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    review_id = Column(String, ForeignKey("reviews.id"), nullable=True)

    # Who raised the dispute
    raised_by = Column(String(255), nullable=False)
    raised_by_email = Column(String(255), default="")
    raised_by_role = Column(String(50), default="contractor")  # contractor, client, engineer, other

    # Dispute details
    title = Column(String(500), nullable=False)
    description = Column(Text, default="")
    dispute_type = Column(String(50), default="design_disagreement")  # design_disagreement, calculation_error, scope_dispute, cost_dispute, safety_concern
    severity = Column(String(20), default="medium")  # critical, high, medium, low

    # What is being disputed
    disputed_item = Column(String(500), default="")  # e.g. "Bearing capacity calculation"
    disputed_value = Column(String(200), default="")  # e.g. "250 kPa"
    proposed_value = Column(String(200), default="")  # e.g. "180 kPa"
    evidence_refs = Column(JSON, default=list)  # file/photo references

    # Resolution
    status = Column(String(30), default="open")  # open, investigating, mediated, resolved, dismissed, escalated
    assigned_to = Column(String, ForeignKey("admin_users.id"), nullable=True)
    resolution_notes = Column(Text, default="")
    resolution_outcome = Column(String(50), default="")  # upheld, overturned, compromise, dismissed

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    assignee = relationship("AdminUser", foreign_keys=[assigned_to], back_populates="dispute_assignments")
    comments = relationship("DisputeComment", back_populates="dispute", cascade="all, delete-orphan")


class DisputeComment(Base):
    """Comment thread on a dispute."""
    __tablename__ = "dispute_comments"

    id = Column(String, primary_key=True)
    dispute_id = Column(String, ForeignKey("disputes.id"), nullable=False)
    author_name = Column(String(255), nullable=False)
    author_email = Column(String(255), default="")
    author_role = Column(String(50), default="admin")  # admin, engineer, contractor, client
    comment = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # internal = admin-only, not visible to parties

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dispute = relationship("Dispute", back_populates="comments")


class BlacklistEntry(Base):
    """Blacklisted entity (contractor, supplier, engineer, etc.)."""
    __tablename__ = "blacklist_entries"

    id = Column(String, primary_key=True)

    # Entity details
    entity_name = Column(String(500), nullable=False)
    entity_type = Column(String(50), default="contractor")  # contractor, supplier, engineer, subconsultant, client
    registration_number = Column(String(200), default="")
    country = Column(String(100), default="")

    # Blacklist reason
    reason = Column(Text, nullable=False)
    reason_category = Column(String(50), default="performance")  # performance, safety_violation, fraud, payment_default, legal, other
    severity = Column(String(20), default="warning")  # warning, restricted, banned

    # Evidence and references
    related_project_ids = Column(JSON, default=list)
    evidence_refs = Column(JSON, default=list)
    incident_date = Column(Date, nullable=True)

    # Who added and approved
    added_by = Column(String(255), nullable=False)
    approved_by = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)  # can be deactivated if entry is overturned

    # Review schedule
    review_date = Column(Date, nullable=True)  # when this entry should be reviewed for removal

    # Notes
    internal_notes = Column(Text, default="")  # admin-only notes

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
