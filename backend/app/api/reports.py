"""Reports API router — Generate PDF/DOCX design reports."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/foundation")
async def generate_foundation_report(project_id: str, format: str = "pdf"):
    """Generate foundation design report."""
    return {"status": "pending", "message": "Report generation will be implemented in Phase 2"}


@router.post("/structural")
async def generate_structural_report(project_id: str, format: str = "pdf"):
    """Generate structural design report."""
    return {"status": "pending", "message": "Report generation will be implemented in Phase 2"}


@router.post("/site-assessment")
async def generate_site_assessment_report(project_id: str, format: str = "pdf"):
    """Generate site assessment report."""
    return {"status": "pending", "message": "Report generation will be implemented in Phase 2"}
