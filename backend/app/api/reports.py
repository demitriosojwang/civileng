"""Reports API router — Generate PDF/DOCX design reports from pipeline results."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.pipeline.site_to_design import SiteAssessmentInput, run_site_assessment_pipeline
from app.reports.pdf_generator import generate_foundation_design_report

router = APIRouter()


@router.post("/foundation/pdf")
async def generate_foundation_pdf(assessment: SiteAssessmentInput):
    """Run the full site assessment pipeline and generate a PDF foundation design report."""
    try:
        # Run pipeline
        result = run_site_assessment_pipeline(assessment)

        # Generate PDF
        pdf_path = generate_foundation_design_report(
            result=result,
            assessment=assessment.dict(),
        )

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"foundation_report_{assessment.project_id}.pdf",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.post("/pipeline")
async def run_pipeline(assessment: SiteAssessmentInput):
    """Run the full site assessment pipeline and return JSON results."""
    try:
        result = run_site_assessment_pipeline(assessment)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")
