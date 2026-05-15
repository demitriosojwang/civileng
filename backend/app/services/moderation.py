"""
Moderation service — business logic for reviews, disputes, and blacklist.
Handles in-memory storage for development; will be backed by PostgreSQL in production.
"""

import uuid
from datetime import datetime, date
from typing import Optional, List, Dict

from app.schemas.moderation import (
    ReviewCreate, ReviewUpdate, ReviewResponse, ReviewStatus,
    ReviewActionCreate, ReviewActionResponse, ReviewActionType,
    DisputeCreate, DisputeUpdate, DisputeResponse, DisputeStatus,
    DisputeCommentCreate, DisputeCommentResponse,
    BlacklistEntryCreate, BlacklistEntryUpdate, BlacklistEntryResponse,
    ModerationStats, AdminUserCreate, AdminUserResponse,
)

# ─── In-memory stores (replace with PostgreSQL via SQLAlchemy in production) ───

_reviews: Dict[str, dict] = {}
_review_actions: Dict[str, dict] = {}
_disputes: Dict[str, dict] = {}
_dispute_comments: Dict[str, dict] = {}
_blacklist: Dict[str, dict] = {}
_admin_users: Dict[str, dict] = {}

# Seed some demo admin users
_admin_users["admin_001"] = {
    "id": "admin_001",
    "email": "admin@civileng.app",
    "display_name": "Sarah Kimani",
    "role": "super_admin",
    "is_active": True,
    "last_login": datetime.utcnow(),
    "created_at": datetime.utcnow(),
}
_admin_users["admin_002"] = {
    "id": "admin_002",
    "email": "moderator@civileng.app",
    "display_name": "James Ochieng",
    "role": "moderator",
    "is_active": True,
    "last_login": None,
    "created_at": datetime.utcnow(),
}


def _gen_id(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:12]}"


# ═══════════════════════════════════════════════════════════════
# ADMIN USERS
# ═══════════════════════════════════════════════════════════════

def list_admin_users() -> List[AdminUserResponse]:
    return [AdminUserResponse(**u) for u in _admin_users.values()]


def get_admin_user(admin_id: str) -> Optional[AdminUserResponse]:
    if admin_id in _admin_users:
        return AdminUserResponse(**_admin_users[admin_id])
    return None


def create_admin_user(data: AdminUserCreate) -> AdminUserResponse:
    admin_id = _gen_id("adm_")
    user = {
        "id": admin_id,
        "email": data.email,
        "display_name": data.display_name,
        "role": data.role.value,
        "is_active": True,
        "last_login": None,
        "created_at": datetime.utcnow(),
    }
    _admin_users[admin_id] = user
    return AdminUserResponse(**user)


# ═══════════════════════════════════════════════════════════════
# REVIEWS
# ═══════════════════════════════════════════════════════════════

def list_reviews(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    review_type: Optional[str] = None,
    assigned_reviewer: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """List reviews with optional filters. Returns {items, total}."""
    items = list(_reviews.values())

    if status:
        items = [r for r in items if r["status"] == status]
    if priority:
        items = [r for r in items if r["priority"] == priority]
    if review_type:
        items = [r for r in items if r["review_type"] == review_type]
    if assigned_reviewer:
        items = [r for r in items if r.get("assigned_reviewer") == assigned_reviewer]

    # Sort by created_at descending (newest first)
    items.sort(key=lambda r: r["created_at"], reverse=True)

    total = len(items)
    paged = items[offset : offset + limit]

    # Enrich with actions
    result = []
    for r in paged:
        actions = [
            ReviewActionResponse(**a)
            for a in _review_actions.values()
            if a["review_id"] == r["id"]
        ]
        actions.sort(key=lambda a: a.created_at, reverse=True)
        r_copy = {**r, "actions": [a.model_dump() for a in actions]}
        result.append(ReviewResponse(**r_copy))

    return {"items": result, "total": total}


def get_review(review_id: str) -> Optional[ReviewResponse]:
    if review_id not in _reviews:
        return None
    r = _reviews[review_id]
    actions = [
        ReviewActionResponse(**a)
        for a in _review_actions.values()
        if a["review_id"] == review_id
    ]
    actions.sort(key=lambda a: a.created_at, reverse=True)
    r_copy = {**r, "actions": [a.model_dump() for a in actions]}
    return ReviewResponse(**r_copy)


def create_review(data: ReviewCreate) -> ReviewResponse:
    review_id = _gen_id("rev_")
    review = {
        "id": review_id,
        "project_id": data.project_id,
        "design_id": data.design_id,
        "submitted_by": data.submitted_by,
        "submitted_by_email": data.submitted_by_email,
        "title": data.title,
        "description": data.description,
        "review_type": data.review_type.value,
        "priority": data.priority.value,
        "foundation_type": data.foundation_type,
        "bearing_capacity_kPa": data.bearing_capacity_kPa,
        "total_concrete_m3": data.total_concrete_m3,
        "total_rebar_kg": data.total_rebar_kg,
        "confidence_score": data.confidence_score,
        "standards_used": data.standards_used,
        "compliance_notes": data.compliance_notes,
        "has_warnings": data.has_warnings,
        "warning_count": data.warning_count,
        "status": "pending",
        "assigned_reviewer": None,
        "attachment_ids": data.attachment_ids,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "resolved_at": None,
    }
    _reviews[review_id] = review
    return ReviewResponse(**{**review, "actions": []})


def update_review(review_id: str, data: ReviewUpdate, admin_id: str) -> Optional[ReviewResponse]:
    if review_id not in _reviews:
        return None

    review = _reviews[review_id]
    old_status = review["status"]

    update_data = data.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        review[k] = v

    review["updated_at"] = datetime.utcnow()

    # If status changed, record the transition
    new_status = review["status"]
    if old_status != new_status:
        review["resolved_at"] = datetime.utcnow() if new_status in ("approved", "rejected") else None

        # Auto-create an action record
        action_id = _gen_id("act_")
        action_type = new_status  # approved, rejected, revisions_needed
        if new_status == "revisions_needed":
            action_type = "requested_revision"
        _review_actions[action_id] = {
            "id": action_id,
            "review_id": review_id,
            "admin_id": admin_id,
            "action": action_type,
            "comment": f"Status changed from {old_status} to {new_status}",
            "old_status": old_status,
            "new_status": new_status,
            "created_at": datetime.utcnow(),
            "admin_name": _admin_users.get(admin_id, {}).get("display_name", admin_id),
        }

    return get_review(review_id)


def add_review_action(review_id: str, data: ReviewActionCreate, admin_id: str) -> Optional[ReviewActionResponse]:
    """Add an action (comment, escalation, etc.) to a review."""
    if review_id not in _reviews:
        return None

    review = _reviews[review_id]
    old_status = review["status"]

    # Determine new status based on action
    status_map = {
        ReviewActionType.approved: "approved",
        ReviewActionType.rejected: "rejected",
        ReviewActionType.requested_revision: "revisions_needed",
        ReviewActionType.escalated: "in_review",
        ReviewActionType.assigned: review["status"],  # no status change
        ReviewActionType.commented: review["status"],  # no status change
    }
    new_status = status_map.get(data.action, review["status"])

    # Update review status
    review["status"] = new_status
    review["updated_at"] = datetime.utcnow()
    if new_status in ("approved", "rejected"):
        review["resolved_at"] = datetime.utcnow()

    action_id = _gen_id("act_")
    action = {
        "id": action_id,
        "review_id": review_id,
        "admin_id": admin_id,
        "action": data.action.value,
        "comment": data.comment,
        "old_status": old_status,
        "new_status": new_status,
        "created_at": datetime.utcnow(),
        "admin_name": _admin_users.get(admin_id, {}).get("display_name", admin_id),
    }
    _review_actions[action_id] = action

    return ReviewActionResponse(**action)


# ═══════════════════════════════════════════════════════════════
# DISPUTES
# ═══════════════════════════════════════════════════════════════

def list_disputes(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    dispute_type: Optional[str] = None,
    assigned_to: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    items = list(_disputes.values())

    if status:
        items = [d for d in items if d["status"] == status]
    if severity:
        items = [d for d in items if d["severity"] == severity]
    if dispute_type:
        items = [d for d in items if d["dispute_type"] == dispute_type]
    if assigned_to:
        items = [d for d in items if d.get("assigned_to") == assigned_to]

    items.sort(key=lambda d: d["created_at"], reverse=True)

    total = len(items)
    paged = items[offset : offset + limit]

    result = []
    for d in paged:
        comments = [
            DisputeCommentResponse(**c)
            for c in _dispute_comments.values()
            if c["dispute_id"] == d["id"]
        ]
        comments.sort(key=lambda c: c.created_at)
        d_copy = {
            **d,
            "comments": [c.model_dump() for c in comments],
            "assignee_name": _admin_users.get(d.get("assigned_to", ""), {}).get("display_name"),
        }
        result.append(DisputeResponse(**d_copy))

    return {"items": result, "total": total}


def get_dispute(dispute_id: str) -> Optional[DisputeResponse]:
    if dispute_id not in _disputes:
        return None
    d = _disputes[dispute_id]
    comments = [
        DisputeCommentResponse(**c)
        for c in _dispute_comments.values()
        if c["dispute_id"] == dispute_id
    ]
    comments.sort(key=lambda c: c.created_at)
    d_copy = {
        **d,
        "comments": [c.model_dump() for c in comments],
        "assignee_name": _admin_users.get(d.get("assigned_to", ""), {}).get("display_name"),
    }
    return DisputeResponse(**d_copy)


def create_dispute(data: DisputeCreate) -> DisputeResponse:
    dispute_id = _gen_id("dsp_")
    dispute = {
        "id": dispute_id,
        "project_id": data.project_id,
        "review_id": data.review_id,
        "raised_by": data.raised_by,
        "raised_by_email": data.raised_by_email,
        "raised_by_role": data.raised_by_role,
        "title": data.title,
        "description": data.description,
        "dispute_type": data.dispute_type.value,
        "severity": data.severity.value,
        "disputed_item": data.disputed_item,
        "disputed_value": data.disputed_value,
        "proposed_value": data.proposed_value,
        "evidence_refs": data.evidence_refs,
        "status": "open",
        "assigned_to": None,
        "resolution_notes": "",
        "resolution_outcome": "",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "resolved_at": None,
    }
    _disputes[dispute_id] = dispute
    return DisputeResponse(**{**dispute, "comments": [], "assignee_name": None})


def update_dispute(dispute_id: str, data: DisputeUpdate, admin_id: str) -> Optional[DisputeResponse]:
    if dispute_id not in _disputes:
        return None

    dispute = _disputes[dispute_id]
    update_data = data.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        dispute[k] = v

    dispute["updated_at"] = datetime.utcnow()

    # If resolved, set resolved_at
    if dispute["status"] in ("resolved", "dismissed"):
        dispute["resolved_at"] = datetime.utcnow()

    return get_dispute(dispute_id)


def add_dispute_comment(dispute_id: str, data: DisputeCommentCreate) -> Optional[DisputeCommentResponse]:
    if dispute_id not in _disputes:
        return None

    comment_id = _gen_id("cmt_")
    comment = {
        "id": comment_id,
        "dispute_id": dispute_id,
        "author_name": data.author_name,
        "author_email": data.author_email,
        "author_role": data.author_role,
        "comment": data.comment,
        "is_internal": data.is_internal,
        "created_at": datetime.utcnow(),
    }
    _dispute_comments[comment_id] = comment

    # Update dispute timestamp
    _disputes[dispute_id]["updated_at"] = datetime.utcnow()

    return DisputeCommentResponse(**comment)


# ═══════════════════════════════════════════════════════════════
# BLACKLIST
# ═══════════════════════════════════════════════════════════════

def list_blacklist(
    entity_type: Optional[str] = None,
    severity: Optional[str] = None,
    reason_category: Optional[str] = None,
    is_active: Optional[bool] = True,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    items = list(_blacklist.values())

    if is_active is not None:
        items = [b for b in items if b["is_active"] == is_active]
    if entity_type:
        items = [b for b in items if b["entity_type"] == entity_type]
    if severity:
        items = [b for b in items if b["severity"] == severity]
    if reason_category:
        items = [b for b in items if b["reason_category"] == reason_category]
    if search:
        search_lower = search.lower()
        items = [
            b for b in items
            if search_lower in b["entity_name"].lower()
            or search_lower in b.get("registration_number", "").lower()
        ]

    items.sort(key=lambda b: b["created_at"], reverse=True)

    total = len(items)
    paged = items[offset : offset + limit]

    return {"items": [BlacklistEntryResponse(**b) for b in paged], "total": total}


def get_blacklist_entry(entry_id: str) -> Optional[BlacklistEntryResponse]:
    if entry_id not in _blacklist:
        return None
    return BlacklistEntryResponse(**_blacklist[entry_id])


def create_blacklist_entry(data: BlacklistEntryCreate) -> BlacklistEntryResponse:
    entry_id = _gen_id("blk_")
    entry = {
        "id": entry_id,
        "entity_name": data.entity_name,
        "entity_type": data.entity_type.value,
        "registration_number": data.registration_number,
        "country": data.country,
        "reason": data.reason,
        "reason_category": data.reason_category.value,
        "severity": data.severity.value,
        "related_project_ids": data.related_project_ids,
        "evidence_refs": data.evidence_refs,
        "incident_date": data.incident_date,
        "added_by": data.added_by,
        "approved_by": None,
        "is_active": True,
        "review_date": data.review_date,
        "internal_notes": data.internal_notes,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    _blacklist[entry_id] = entry
    return BlacklistEntryResponse(**entry)


def update_blacklist_entry(entry_id: str, data: BlacklistEntryUpdate) -> Optional[BlacklistEntryResponse]:
    if entry_id not in _blacklist:
        return None

    entry = _blacklist[entry_id]
    update_data = data.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        if k == "entity_type" and v is not None:
            entry[k] = v.value
        elif k == "reason_category" and v is not None:
            entry[k] = v.value
        elif k == "severity" and v is not None:
            entry[k] = v.value
        else:
            entry[k] = v

    entry["updated_at"] = datetime.utcnow()
    return BlacklistEntryResponse(**entry)


def check_blacklist(entity_name: str, registration_number: str = "") -> List[BlacklistEntryResponse]:
    """Check if an entity is on the blacklist. Used during tender submission."""
    results = []
    entity_lower = entity_name.lower()
    reg_lower = registration_number.lower()

    for b in _blacklist.values():
        if not b["is_active"]:
            continue
        if entity_lower in b["entity_name"].lower() or b["entity_name"].lower() in entity_lower:
            results.append(BlacklistEntryResponse(**b))
        elif reg_lower and b.get("registration_number") and reg_lower in b["registration_number"].lower():
            results.append(BlacklistEntryResponse(**b))

    return results


# ═══════════════════════════════════════════════════════════════
# DASHBOARD STATS
# ═══════════════════════════════════════════════════════════════

def get_moderation_stats() -> ModerationStats:
    """Aggregate statistics for the admin dashboard."""
    today = datetime.utcnow().date()

    reviews = list(_reviews.values())
    disputes = list(_disputes.values())
    blacklist_items = list(_blacklist.values())

    # Reviews stats
    reviews_pending = sum(1 for r in reviews if r["status"] == "pending")
    reviews_in_review = sum(1 for r in reviews if r["status"] == "in_review")
    reviews_approved_today = sum(
        1 for r in reviews
        if r["status"] == "approved" and r.get("resolved_at") and r["resolved_at"].date() == today
    )
    reviews_rejected_today = sum(
        1 for r in reviews
        if r["status"] == "rejected" and r.get("resolved_at") and r["resolved_at"].date() == today
    )

    # Disputes stats
    disputes_open = sum(1 for d in disputes if d["status"] == "open")
    disputes_investigating = sum(1 for d in disputes if d["status"] == "investigating")
    disputes_resolved_today = sum(
        1 for d in disputes
        if d["status"] in ("resolved", "dismissed") and d.get("resolved_at") and d["resolved_at"].date() == today
    )
    disputes_critical = sum(1 for d in disputes if d["severity"] == "critical" and d["status"] not in ("resolved", "dismissed"))

    # Blacklist stats
    blacklist_active = sum(1 for b in blacklist_items if b["is_active"])
    blacklist_pending_approval = sum(1 for b in blacklist_items if b["is_active"] and not b.get("approved_by"))
    blacklist_banned = sum(1 for b in blacklist_items if b["is_active"] and b["severity"] == "banned")

    # Recent activity (last 10 actions across all types)
    recent = []

    for a in _review_actions.values():
        recent.append({
            "type": "review_action",
            "id": a["id"],
            "description": f'{a["action"]} by {a.get("admin_name", a["admin_id"])}',
            "timestamp": a["created_at"],
        })

    for c in _dispute_comments.values():
        recent.append({
            "type": "dispute_comment",
            "id": c["id"],
            "description": f'Comment by {c["author_name"]} on dispute',
            "timestamp": c["created_at"],
        })

    recent.sort(key=lambda x: x["timestamp"], reverse=True)
    recent = recent[:10]

    return ModerationStats(
        reviews_pending=reviews_pending,
        reviews_in_review=reviews_in_review,
        reviews_approved_today=reviews_approved_today,
        reviews_rejected_today=reviews_rejected_today,
        reviews_total=len(reviews),
        disputes_open=disputes_open,
        disputes_investigating=disputes_investigating,
        disputes_resolved_today=disputes_resolved_today,
        disputes_critical=disputes_critical,
        disputes_total=len(disputes),
        blacklist_active=blacklist_active,
        blacklist_pending_approval=blacklist_pending_approval,
        blacklist_banned=blacklist_banned,
        blacklist_total=len(blacklist_items),
        recent_activity=recent,
    )
