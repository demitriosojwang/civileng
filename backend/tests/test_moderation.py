"""
Tests for the Admin Moderation module.
Tests review, dispute, and blacklist CRUD operations.
"""

import pytest
from fastapi.testclient import TestClient
from app import app


client = TestClient(app)


class TestModerationHealth:
    def test_health(self):
        res = client.get("/api/moderation/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert data["module"] == "moderation"


class TestDashboardStats:
    def test_get_stats(self):
        res = client.get("/api/moderation/stats")
        assert res.status_code == 200
        data = res.json()
        assert "reviews_pending" in data
        assert "disputes_open" in data
        assert "blacklist_active" in data


class TestReviews:
    def test_create_review(self):
        res = client.post("/api/moderation/reviews", json={
            "project_id": "proj_test_001",
            "submitted_by": "Eng. Wanjiku",
            "submitted_by_email": "wanjiku@example.com",
            "title": "Pad Foundation Design — Block A",
            "description": "Foundation design for Block A residential building",
            "review_type": "design_approval",
            "priority": "high",
            "foundation_type": "pad",
            "bearing_capacity_kPa": 250.0,
            "total_concrete_m3": 45.2,
            "total_rebar_kg": 3200.0,
            "confidence_score": 0.92,
            "standards_used": ["BS 8004", "BS 8110"],
            "compliance_notes": "All checks pass. Factor of safety = 3.0.",
            "has_warnings": False,
            "warning_count": 0,
        })
        assert res.status_code == 201
        data = res.json()
        assert data["id"].startswith("rev_")
        assert data["status"] == "pending"
        assert data["foundation_type"] == "pad"
        assert data["bearing_capacity_kPa"] == 250.0
        return data["id"]

    def test_list_reviews(self):
        res = client.get("/api/moderation/reviews")
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert "total" in data

    def test_list_reviews_filtered(self):
        res = client.get("/api/moderation/reviews?status=pending")
        assert res.status_code == 200
        data = res.json()
        assert all(r["status"] == "pending" for r in data["items"])

    def test_get_review(self):
        # Create first
        create_res = client.post("/api/moderation/reviews", json={
            "project_id": "proj_test_002",
            "submitted_by": "Eng. Odhiambo",
            "title": "Raft Foundation — Commercial",
            "review_type": "calculation_check",
        })
        review_id = create_res.json()["id"]

        res = client.get(f"/api/moderation/reviews/{review_id}")
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == review_id

    def test_approve_review(self):
        # Create
        create_res = client.post("/api/moderation/reviews", json={
            "project_id": "proj_test_003",
            "submitted_by": "Eng. Achieng",
            "title": "Strip Foundation Check",
            "review_type": "design_approval",
        })
        review_id = create_res.json()["id"]

        # Approve
        res = client.post(
            f"/api/moderation/reviews/{review_id}/actions?admin_id=admin_001",
            json={"action": "approved", "comment": "Looks good, approved."},
        )
        assert res.status_code == 201
        data = res.json()
        assert data["action"] == "approved"
        assert data["new_status"] == "approved"

    def test_reject_review(self):
        create_res = client.post("/api/moderation/reviews", json={
            "project_id": "proj_test_004",
            "submitted_by": "Eng. Kamau",
            "title": "Pile Foundation — Safety Concern",
            "review_type": "design_approval",
            "has_warnings": True,
            "warning_count": 2,
        })
        review_id = create_res.json()["id"]

        res = client.post(
            f"/api/moderation/reviews/{review_id}/actions?admin_id=admin_001",
            json={"action": "rejected", "comment": "Insufficient bearing capacity. Revise and resubmit."},
        )
        assert res.status_code == 201
        assert res.json()["action"] == "rejected"

    def test_request_revision(self):
        create_res = client.post("/api/moderation/reviews", json={
            "project_id": "proj_test_005",
            "submitted_by": "Eng. Njeri",
            "title": "Report Review — Phase 1",
            "review_type": "report_review",
        })
        review_id = create_res.json()["id"]

        res = client.post(
            f"/api/moderation/reviews/{review_id}/actions?admin_id=admin_001",
            json={"action": "requested_revision", "comment": "Add SPT test results to appendix."},
        )
        assert res.status_code == 201
        assert res.json()["new_status"] == "revisions_needed"

    def test_review_not_found(self):
        res = client.get("/api/moderation/reviews/nonexistent_id")
        assert res.status_code == 404


class TestDisputes:
    def test_create_dispute(self):
        res = client.post("/api/moderation/disputes", json={
            "project_id": "proj_test_001",
            "raised_by": "BuildRight Contractors",
            "raised_by_email": "buildright@example.com",
            "raised_by_role": "contractor",
            "title": "Bearing Capacity Disagreement",
            "description": "We believe the bearing capacity of 250 kPa is too high for this soil type.",
            "dispute_type": "design_disagreement",
            "severity": "high",
            "disputed_item": "Bearing capacity calculation",
            "disputed_value": "250 kPa",
            "proposed_value": "180 kPa",
        })
        assert res.status_code == 201
        data = res.json()
        assert data["id"].startswith("dsp_")
        assert data["status"] == "open"
        assert data["severity"] == "high"
        return data["id"]

    def test_list_disputes(self):
        res = client.get("/api/moderation/disputes")
        assert res.status_code == 200
        data = res.json()
        assert "items" in data

    def test_add_comment(self):
        # Create dispute
        create_res = client.post("/api/moderation/disputes", json={
            "project_id": "proj_test_002",
            "raised_by": "SafeBuild Ltd",
            "title": "Safety Concern — Expansive Soil",
            "dispute_type": "safety_concern",
            "severity": "critical",
        })
        dispute_id = create_res.json()["id"]

        # Add comment
        res = client.post(f"/api/moderation/disputes/{dispute_id}/comments", json={
            "comment": "Requesting additional soil tests before proceeding.",
            "author_name": "Sarah Kimani",
            "author_role": "admin",
            "is_internal": True,
        })
        assert res.status_code == 201
        assert res.json()["is_internal"] is True

    def test_resolve_dispute(self):
        create_res = client.post("/api/moderation/disputes", json={
            "project_id": "proj_test_003",
            "raised_by": "Client Corp",
            "raised_by_role": "client",
            "title": "Cost Dispute — Additional Piling",
            "dispute_type": "cost_dispute",
            "severity": "medium",
        })
        dispute_id = create_res.json()["id"]

        # Resolve
        res = client.patch(
            f"/api/moderation/disputes/{dispute_id}?admin_id=admin_001",
            json={
                "status": "resolved",
                "resolution_outcome": "compromise",
                "resolution_notes": "Split additional piling cost 60/40 between client and contractor.",
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "resolved"
        assert data["resolution_outcome"] == "compromise"

    def test_dispute_not_found(self):
        res = client.get("/api/moderation/disputes/nonexistent_id")
        assert res.status_code == 404


class TestBlacklist:
    def test_add_to_blacklist(self):
        res = client.post("/api/moderation/blacklist", json={
            "entity_name": "Shoddy Builders Ltd",
            "entity_type": "contractor",
            "registration_number": "REG-2021-0456",
            "country": "Kenya",
            "reason": "Repeated structural failures on 3 projects. Concrete quality consistently below specification.",
            "reason_category": "safety_violation",
            "severity": "banned",
            "added_by": "admin_001",
            "internal_notes": "Reported by 2 separate clients. NCA notified.",
        })
        assert res.status_code == 201
        data = res.json()
        assert data["id"].startswith("blk_")
        assert data["severity"] == "banned"
        assert data["is_active"] is True
        assert data["approved_by"] is None
        return data["id"]

    def test_list_blacklist(self):
        res = client.get("/api/moderation/blacklist")
        assert res.status_code == 200
        data = res.json()
        assert "items" in data

    def test_approve_blacklist_entry(self):
        # Create
        create_res = client.post("/api/moderation/blacklist", json={
            "entity_name": "LatePay Suppliers",
            "entity_type": "supplier",
            "reason": "Consistent late deliveries causing project delays.",
            "reason_category": "performance",
            "severity": "restricted",
            "added_by": "admin_002",
        })
        entry_id = create_res.json()["id"]

        # Approve
        res = client.patch(f"/api/moderation/blacklist/{entry_id}", json={
            "approved_by": "admin_001",
        })
        assert res.status_code == 200
        assert res.json()["approved_by"] == "admin_001"

    def test_deactivate_blacklist_entry(self):
        create_res = client.post("/api/moderation/blacklist", json={
            "entity_name": "Reformed Engineering Co",
            "entity_type": "engineer",
            "reason": "Temporary suspension due to license lapse.",
            "reason_category": "legal",
            "severity": "restricted",
            "added_by": "admin_001",
        })
        entry_id = create_res.json()["id"]

        res = client.patch(f"/api/moderation/blacklist/{entry_id}", json={
            "is_active": False,
        })
        assert res.status_code == 200
        assert res.json()["is_active"] is False

    def test_check_blacklist_found(self):
        # Add
        client.post("/api/moderation/blacklist", json={
            "entity_name": "FraudCorp International",
            "entity_type": "contractor",
            "reason": "Documented fraud in tender submissions.",
            "reason_category": "fraud",
            "severity": "banned",
            "added_by": "admin_001",
        })

        # Check
        res = client.get("/api/moderation/blacklist/check?entity_name=FraudCorp")
        assert res.status_code == 200
        data = res.json()
        assert data["is_blacklisted"] is True
        assert len(data["matches"]) > 0

    def test_check_blacklist_not_found(self):
        res = client.get("/api/moderation/blacklist/check?entity_name=Honest+Builders+Inc")
        assert res.status_code == 200
        data = res.json()
        assert data["is_blacklisted"] is False

    def test_blacklist_not_found(self):
        res = client.get("/api/moderation/blacklist/nonexistent_id")
        assert res.status_code == 404


class TestAdminUsers:
    def test_list_admin_users(self):
        res = client.get("/api/moderation/users")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 2  # Seeded users

    def test_create_admin_user(self):
        res = client.post("/api/moderation/users", json={
            "email": "newadmin@civileng.app",
            "display_name": "Grace Muthoni",
            "role": "moderator",
        })
        assert res.status_code == 201
        assert res.json()["email"] == "newadmin@civileng.app"
