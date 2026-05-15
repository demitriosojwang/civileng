"""
Admin Moderation API router — reviews, disputes, blacklist, and dashboard stats.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from app.schemas.moderation import (
    AdminUserCreate, AdminUserResponse,
    ReviewCreate, ReviewUpdate, ReviewResponse,
    ReviewActionCreate, ReviewActionResponse,
    DisputeCreate, DisputeUpdate, DisputeResponse,
    DisputeCommentCreate, DisputeCommentResponse,
    BlacklistEntryCreate, BlacklistEntryUpdate, BlacklistEntryResponse,
    ModerationStats,
)
from app.services import moderation

router = APIRouter()


# ─── Health ───

@router.get("/health")
async def moderation_health():
    return {"status": "ok", "module": "moderation"}


# ═══════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════

@router.get("/stats", response_model=ModerationStats)
async def get_dashboard_stats():
    """Get moderation dashboard statistics."""
    return moderation.get_moderation_stats()


# ═══════════════════════════════════════════════════════════════
# ADMIN USERS
# ═══════════════════════════════════════════════════════════════

@router.get("/users", response_model=list[AdminUserResponse])
async def list_admin_users():
    """List all admin/moderator users."""
    return moderation.list_admin_users()


@router.post("/users", response_model=AdminUserResponse, status_code=201)
async def create_admin_user(data: AdminUserCreate):
    """Create a new admin/moderator user."""
    return moderation.create_admin_user(data)


@router.get("/users/{admin_id}", response_model=AdminUserResponse)
async def get_admin_user(admin_id: str):
    """Get a specific admin user."""
    user = moderation.get_admin_user(admin_id)
    if not user:
        raise HTTPException(status_code=404, detail="Admin user not found")
    return user


# ═══════════════════════════════════════════════════════════════
# REVIEWS
# ═══════════════════════════════════════════════════════════════

@router.get("/reviews")
async def list_reviews(
    status: Optional[str] = Query(None, description="Filter by status: pending, in_review, approved, rejected, revisions_needed"),
    priority: Optional[str] = Query(None, description="Filter by priority: urgent, high, normal, low"),
    review_type: Optional[str] = Query(None, description="Filter by type: design_approval, calculation_check, report_review"),
    assigned_reviewer: Optional[str] = Query(None, description="Filter by assigned reviewer"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List reviews with optional filters."""
    return moderation.list_reviews(
        status=status,
        priority=priority,
        review_type=review_type,
        assigned_reviewer=assigned_reviewer,
        limit=limit,
        offset=offset,
    )


@router.post("/reviews", response_model=ReviewResponse, status_code=201)
async def create_review(data: ReviewCreate):
    """Submit a new design/calculation for review."""
    return moderation.create_review(data)


@router.get("/reviews/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: str):
    """Get a specific review with its action history."""
    review = moderation.get_review(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.patch("/reviews/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: str,
    data: ReviewUpdate,
    admin_id: str = Query("admin_001", description="ID of admin performing the update"),
):
    """Update a review (status, priority, assignment, etc.)."""
    review = moderation.update_review(review_id, data, admin_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.post("/reviews/{review_id}/actions", response_model=ReviewActionResponse, status_code=201)
async def add_review_action(
    review_id: str,
    data: ReviewActionCreate,
    admin_id: str = Query("admin_001", description="ID of admin performing the action"),
):
    """Add an action to a review (approve, reject, comment, escalate, etc.)."""
    action = moderation.add_review_action(review_id, data, admin_id)
    if not action:
        raise HTTPException(status_code=404, detail="Review not found")
    return action


# ═══════════════════════════════════════════════════════════════
# DISPUTES
# ═══════════════════════════════════════════════════════════════

@router.get("/disputes")
async def list_disputes(
    status: Optional[str] = Query(None, description="Filter by status: open, investigating, mediated, resolved, dismissed, escalated"),
    severity: Optional[str] = Query(None, description="Filter by severity: critical, high, medium, low"),
    dispute_type: Optional[str] = Query(None, description="Filter by type: design_disagreement, calculation_error, scope_dispute, cost_dispute, safety_concern"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned admin"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List disputes with optional filters."""
    return moderation.list_disputes(
        status=status,
        severity=severity,
        dispute_type=dispute_type,
        assigned_to=assigned_to,
        limit=limit,
        offset=offset,
    )


@router.post("/disputes", response_model=DisputeResponse, status_code=201)
async def create_dispute(data: DisputeCreate):
    """Raise a new dispute."""
    return moderation.create_dispute(data)


@router.get("/disputes/{dispute_id}", response_model=DisputeResponse)
async def get_dispute(dispute_id: str):
    """Get a specific dispute with comments."""
    dispute = moderation.get_dispute(dispute_id)
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
    return dispute


@router.patch("/disputes/{dispute_id}", response_model=DisputeResponse)
async def update_dispute(
    dispute_id: str,
    data: DisputeUpdate,
    admin_id: str = Query("admin_001", description="ID of admin performing the update"),
):
    """Update a dispute (assign, resolve, change severity, etc.)."""
    dispute = moderation.update_dispute(dispute_id, data, admin_id)
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
    return dispute


@router.post("/disputes/{dispute_id}/comments", response_model=DisputeCommentResponse, status_code=201)
async def add_dispute_comment(
    dispute_id: str,
    data: DisputeCommentCreate,
):
    """Add a comment to a dispute thread."""
    comment = moderation.add_dispute_comment(dispute_id, data)
    if not comment:
        raise HTTPException(status_code=404, detail="Dispute not found")
    return comment


# ═══════════════════════════════════════════════════════════════
# BLACKLIST
# ═══════════════════════════════════════════════════════════════

@router.get("/blacklist")
async def list_blacklist(
    entity_type: Optional[str] = Query(None, description="Filter by entity type: contractor, supplier, engineer, subconsultant, client"),
    severity: Optional[str] = Query(None, description="Filter by severity: warning, restricted, banned"),
    reason_category: Optional[str] = Query(None, description="Filter by reason: performance, safety_violation, fraud, payment_default, legal, other"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search entity name or registration number"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List blacklist entries with optional filters."""
    return moderation.list_blacklist(
        entity_type=entity_type,
        severity=severity,
        reason_category=reason_category,
        is_active=is_active,
        search=search,
        limit=limit,
        offset=offset,
    )


@router.post("/blacklist", response_model=BlacklistEntryResponse, status_code=201)
async def create_blacklist_entry(data: BlacklistEntryCreate):
    """Add an entity to the blacklist."""
    return moderation.create_blacklist_entry(data)


@router.get("/blacklist/check")
async def check_blacklist(
    entity_name: str = Query(..., description="Entity name to check"),
    registration_number: str = Query("", description="Registration number to check"),
):
    """Check if an entity is on the blacklist. Used during tender submission."""
    results = moderation.check_blacklist(entity_name, registration_number)
    return {
        "entity_name": entity_name,
        "is_blacklisted": len(results) > 0,
        "matches": results,
    }


@router.get("/blacklist/{entry_id}", response_model=BlacklistEntryResponse)
async def get_blacklist_entry(entry_id: str):
    """Get a specific blacklist entry."""
    entry = moderation.get_blacklist_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Blacklist entry not found")
    return entry


@router.patch("/blacklist/{entry_id}", response_model=BlacklistEntryResponse)
async def update_blacklist_entry(
    entry_id: str,
    data: BlacklistEntryUpdate,
):
    """Update a blacklist entry (approve, deactivate, change severity, etc.)."""
    entry = moderation.update_blacklist_entry(entry_id, data)
    if not entry:
        raise HTTPException(status_code=404, detail="Blacklist entry not found")
    return entry
