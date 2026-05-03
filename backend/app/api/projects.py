"""Projects API router — CRUD operations for construction projects."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_projects():
    """List all projects."""
    return {"projects": [], "total": 0}


@router.post("/")
async def create_project(project: dict):
    """Create a new construction project."""
    return {"id": "proj_001", "status": "created", "project": project}


@router.get("/{project_id}")
async def get_project(project_id: str):
    """Get project details."""
    return {"id": project_id, "name": "Example Project", "status": "active"}
