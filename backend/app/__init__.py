"""
CivilEng — AI-Powered Foundation & Structural Design Software
Backend Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import foundation, structural, soil, materials, projects, reports
from app.core.config import settings

app = FastAPI(
    title="CivilEng API",
    description="Foundation and structural design calculation engine for construction tendering",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(foundation.router, prefix="/api/foundation", tags=["Foundation Design"])
app.include_router(structural.router, prefix="/api/structural", tags=["Structural Design"])
app.include_router(soil.router, prefix="/api/soil", tags=["Soil Classification"])
app.include_router(materials.router, prefix="/api/materials", tags=["Material Quantities"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/api/standards")
async def supported_standards():
    """Return all engineering standards supported by the calculation engine."""
    return {
        "standards": [
            {"code": "BS 8004", "description": "Code of practice for foundations", "year": 2015},
            {"code": "BS 8110", "description": "Structural use of concrete", "year": 1997},
            {"code": "BS 5930", "description": "Code of practice for ground investigations", "year": 2015},
            {"code": "BS 6399", "description": "Loading for buildings", "year": 1996},
            {"code": "EN 1990", "description": "Eurocode 0 — Basis of structural design", "year": 2002},
            {"code": "EN 1992", "description": "Eurocode 2 — Design of concrete structures", "year": 2004},
            {"code": "EN 1997", "description": "Eurocode 7 — Geotechnical design", "year": 2004},
            {"code": "ISO 14688", "description": "Geotechnical identification and classification", "year": 2017},
        ]
    }
