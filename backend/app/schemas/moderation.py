"""
Pydantic schemas for the Admin Moderation module.
Handles request/response validation for reviews, disputes, and blacklist.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


# ─── Enums ───

class AdminRole(str, Enum):
    super_admin = "super_admin"
    admin = "admin"
    moderator = "moderator"
    viewer = "viewer"


class ReviewType(str, Enum):
    design_approval = "design_approval"
    calculation_check = "calculation_check"
    report_review = "report_review"


class ReviewPriority(str, Enum):
    urgent = "urgent"
    high = "high"
    normal = "normal"
    low = "low"


class ReviewStatus(str, Enum):
    pending = "pending"
    in_review = "in_review"
    approved = "approved"
    rejected = "rejected"
    revisions_needed = "revisions_needed"


class ReviewActionType(str, Enum):
    approved = "approved"
    rejected = "rejected"
    requested_revision = "requested_revision"
    commented = "commented"
    escalated = "escalated"
    assigned = "assigned"


class DisputeType(str, Enum):
    design_disagreement = "design_disagreement"
    calculation_error = "calculation_error"
    scope_dispute = "scope_dispute"
    cost_dispute = "cost_dispute"
    safety_concern = "safety_concern"


class DisputeSeverity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class DisputeStatus(str, Enum):
    open = "open"
    investigating = "investigating"
    mediated = "mediated"
    resolved = "resolved"
    dismissed = "dismissed"
    escalated = "escalated"


class DisputeOutcome(str, Enum):
    upheld = "upheld"
    overturned = "overturned"
    compromise = "compromise"
    dismissed = "dismissed"


class EntityType(str, Enum):
    contractor = "contractor"
    supplier = "supplier"
    engineer = "engineer"
    subconsultant = "subconsultant"
    client = "client"


class BlacklistReasonCategory(str, Enum):
    performance = "performance"
    safety_violation = "safety_violation"
    fraud = "fraud"
    payment_default = "payment_default"
    legal = "legal"
    other = "other"


class BlacklistSeverity(str, Enum):
    warning = "warning"
    restricted = "restricted"
    banned = "banned"


# ─── Admin User Schemas ───

class AdminUserBase(BaseModel):
    email: str
    display_name: str = ""
    role: AdminRole = AdminRole.moderator


class AdminUserCreate(AdminUserBase):
    pass


class AdminUserResponse(AdminUserBase):
    id: str
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Review Schemas ───

class ReviewCreate(BaseModel):
    project_id: str
    design_id: Optional[str] = None
    submitted_by: str
    submitted_by_email: str = ""
    title: str = ""
    description: str = ""
    review_type: ReviewType = ReviewType.design_approval
    priority: ReviewPriority = ReviewPriority.normal
    foundation_type: str = ""
    bearing_capacity_kPa: Optional[float] = None
    total_concrete_m3: Optional[float] = None
    total_rebar_kg: Optional[float] = None
    confidence_score: Optional[float] = None
    standards_used: List[str] = []
    compliance_notes: str = ""
    has_warnings: bool = False
    warning_count: int = 0
    attachment_ids: List[str] = []


class ReviewUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    review_type: Optional[ReviewType] = None
    priority: Optional[ReviewPriority] = None
    status: Optional[ReviewStatus] = None
    assigned_reviewer: Optional[str] = None
    compliance_notes: Optional[str] = None


class ReviewResponse(BaseModel):
    id: str
    project_id: str
    design_id: Optional[str] = None
    submitted_by: str
    submitted_by_email: str = ""
    title: str = ""
    description: str = ""
    review_type: str = "design_approval"
    priority: str = "normal"
    foundation_type: str = ""
    bearing_capacity_kPa: Optional[float] = None
    total_concrete_m3: Optional[float] = None
    total_rebar_kg: Optional[float] = None
    confidence_score: Optional[float] = None
    standards_used: List[str] = []
    compliance_notes: str = ""
    has_warnings: bool = False
    warning_count: int = 0
    status: str = "pending"
    assigned_reviewer: Optional[str] = None
    attachment_ids: List[str] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    actions: List["ReviewActionResponse"] = []

    class Config:
        from_attributes = True


class ReviewActionCreate(BaseModel):
    action: ReviewActionType
    comment: str = ""


class ReviewActionResponse(BaseModel):
    id: str
    review_id: str
    admin_id: str
    action: str
    comment: str = ""
    old_status: str = ""
    new_status: str = ""
    created_at: datetime
    admin_name: Optional[str] = None

    class Config:
        from_attributes = True


# ─── Dispute Schemas ───

class DisputeCreate(BaseModel):
    project_id: str
    review_id: Optional[str] = None
    raised_by: str
    raised_by_email: str = ""
    raised_by_role: str = "contractor"
    title: str
    description: str = ""
    dispute_type: DisputeType = DisputeType.design_disagreement
    severity: DisputeSeverity = DisputeSeverity.medium
    disputed_item: str = ""
    disputed_value: str = ""
    proposed_value: str = ""
    evidence_refs: List[str] = []


class DisputeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    dispute_type: Optional[DisputeType] = None
    severity: Optional[DisputeSeverity] = None
    status: Optional[DisputeStatus] = None
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolution_outcome: Optional[DisputeOutcome] = None


class DisputeResponse(BaseModel):
    id: str
    project_id: str
    review_id: Optional[str] = None
    raised_by: str
    raised_by_email: str = ""
    raised_by_role: str = "contractor"
    title: str
    description: str = ""
    dispute_type: str = "design_disagreement"
    severity: str = "medium"
    disputed_item: str = ""
    disputed_value: str = ""
    proposed_value: str = ""
    evidence_refs: List[str] = []
    status: str = "open"
    assigned_to: Optional[str] = None
    resolution_notes: str = ""
    resolution_outcome: str = ""
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    comments: List["DisputeCommentResponse"] = []
    assignee_name: Optional[str] = None

    class Config:
        from_attributes = True


class DisputeCommentCreate(BaseModel):
    comment: str
    author_name: str
    author_email: str = ""
    author_role: str = "admin"
    is_internal: bool = False


class DisputeCommentResponse(BaseModel):
    id: str
    dispute_id: str
    author_name: str
    author_email: str = ""
    author_role: str = "admin"
    comment: str
    is_internal: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Blacklist Schemas ───

class BlacklistEntryCreate(BaseModel):
    entity_name: str
    entity_type: EntityType = EntityType.contractor
    registration_number: str = ""
    country: str = ""
    reason: str
    reason_category: BlacklistReasonCategory = BlacklistReasonCategory.performance
    severity: BlacklistSeverity = BlacklistSeverity.warning
    related_project_ids: List[str] = []
    evidence_refs: List[str] = []
    incident_date: Optional[date] = None
    added_by: str
    internal_notes: str = ""
    review_date: Optional[date] = None


class BlacklistEntryUpdate(BaseModel):
    entity_name: Optional[str] = None
    entity_type: Optional[EntityType] = None
    registration_number: Optional[str] = None
    country: Optional[str] = None
    reason: Optional[str] = None
    reason_category: Optional[BlacklistReasonCategory] = None
    severity: Optional[BlacklistSeverity] = None
    is_active: Optional[bool] = None
    approved_by: Optional[str] = None
    internal_notes: Optional[str] = None
    review_date: Optional[date] = None


class BlacklistEntryResponse(BaseModel):
    id: str
    entity_name: str
    entity_type: str = "contractor"
    registration_number: str = ""
    country: str = ""
    reason: str
    reason_category: str = "performance"
    severity: str = "warning"
    related_project_ids: List[str] = []
    evidence_refs: List[str] = []
    incident_date: Optional[date] = None
    added_by: str
    approved_by: Optional[str] = None
    is_active: bool = True
    review_date: Optional[date] = None
    internal_notes: str = ""
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Dashboard Stats ───

class ModerationStats(BaseModel):
    """Summary statistics for the admin dashboard."""
    reviews_pending: int = 0
    reviews_in_review: int = 0
    reviews_approved_today: int = 0
    reviews_rejected_today: int = 0
    reviews_total: int = 0

    disputes_open: int = 0
    disputes_investigating: int = 0
    disputes_resolved_today: int = 0
    disputes_critical: int = 0
    disputes_total: int = 0

    blacklist_active: int = 0
    blacklist_pending_approval: int = 0
    blacklist_banned: int = 0
    blacklist_total: int = 0

    recent_activity: List[dict] = []


# Resolve forward references
ReviewResponse.model_rebuild()
DisputeResponse.model_rebuild()
