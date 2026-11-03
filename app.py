"""
Resumely AI — Application Server (FastAPI)
"""

import os
import uuid
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from report import generate_pdf_report

from config import (
    BASE_DIR,
    HOST,
    PORT,
    DEBUG,
    SCORING_CRITERIA,
    CREATOR_INFO,
    GEMINI_MODEL,
    MAX_FILE_SIZE_MB
)
from extractor import (
    process_resume_upload,
    ExtractionError,
    EmptyExtractionError
)
from analyzer import analyze_resume, AnalysisError, RateLimitError
from database import init_db, save_analysis, get_analysis, list_recent_analyses

# Initialize Database
init_db()

# Initialize FastAPI App
app = FastAPI(
    title="Resumely AI",
    description="Editorial ATS Resume Analyzer Web Application",
    version="1.0.0"
)

# In-Memory Active Jobs Store for Real-Time Backend Progress
ACTIVE_JOBS: Dict[str, Dict[str, Any]] = {}

async def execute_analysis_pipeline(
    job_id: str,
    file_bytes: bytes,
    filename: str,
    target_role: Optional[str],
    job_description: Optional[str]
):
    """
    Background worker that executes real analysis steps, driving live progress.
    """
    try:
        # Step 1: Text Extraction (PyMuPDF / OCR)
        ACTIVE_JOBS[job_id] = {
            "status": "processing",
            "step": 1,
            "message": "Extracting text from document...",
            "analysis_id": None,
            "error": None
        }
        await asyncio.sleep(0.3)  # Yield for UI update
        extraction = process_resume_upload(file_bytes, filename)

        # Step 2: ATS Parsing & Format Check
        ACTIVE_JOBS[job_id]["step"] = 2
        ACTIVE_JOBS[job_id]["message"] = "Auditing ATS format and layout structure..."
        await asyncio.sleep(0.4)

        # Step 3: Role & Keyword Alignment Evaluation
        ACTIVE_JOBS[job_id]["step"] = 3
        ACTIVE_JOBS[job_id]["message"] = "Matching credentials against role & keyword taxonomy..."
        analysis_model = analyze_resume(
            resume_text=extraction.text,
            target_role=target_role,
            job_description=job_description
        )

        # Step 4: Synthesizing Improvements & Finalizing
        ACTIVE_JOBS[job_id]["step"] = 4
        ACTIVE_JOBS[job_id]["message"] = "Finding prioritized suggestions & bullet rewrites..."
        await asyncio.sleep(0.3)

        analysis_id = uuid.uuid4().hex
        save_analysis(
            analysis_id=analysis_id,
            filename=filename,
            target_role=target_role,
            job_description=job_description,
            analysis_data=analysis_model.model_dump()
        )

        ACTIVE_JOBS[job_id]["status"] = "completed"
        ACTIVE_JOBS[job_id]["analysis_id"] = analysis_id
        ACTIVE_JOBS[job_id]["redirect_url"] = f"/results/{analysis_id}"

    except Exception as e:
        ACTIVE_JOBS[job_id]["status"] = "failed"
        ACTIVE_JOBS[job_id]["error"] = str(e)


@app.post("/api/analyze")
async def start_analysis_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_role: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None)
):
    """
    Initiates real background analysis and returns a job tracking token.
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="A resume document is required.")

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    job_id = uuid.uuid4().hex
    ACTIVE_JOBS[job_id] = {
        "status": "pending",
        "step": 0,
        "message": "Initializing analysis pipeline...",
        "analysis_id": None,
        "error": None
    }

    background_tasks.add_task(
        execute_analysis_pipeline,
        job_id=job_id,
        file_bytes=file_bytes,
        filename=file.filename,
        target_role=target_role,
        job_description=job_description
    )

    return {"job_id": job_id, "status": "pending"}


@app.get("/api/analyze/status/{job_id}")
async def get_analysis_status(job_id: str):
    """
    Returns real-time progress for the active analysis job.
    """
    job = ACTIVE_JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Analysis job not found.")
    return job


@app.get("/results/{analysis_id}", response_class=HTMLResponse)
async def view_results_page(request: Request, analysis_id: str):
    """
    Renders the comprehensive diagnostic results page for a given analysis record.
    """
    record = get_analysis(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis report not found.")

    return templates.TemplateResponse(
        request=request,
        name="results.html",
        context={
            "record": record,
            "analysis": record["analysis"]
        }
    )


@app.get("/report/{analysis_id}/download")
async def download_pdf_report(analysis_id: str):
    """
    Generates and downloads the editorial PDF audit report.
    """
    record = get_analysis(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis report not found.")

    try:
        pdf_bytes = generate_pdf_report(record, record["analysis"])
        safe_filename = f"Resumely_Audit_{record.get('filename', 'report').replace('.pdf', '')}_{analysis_id[:6]}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{safe_filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {e}")



@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    """Custom 404 page styled with design tokens."""
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=404, content={"detail": exc.detail or "Resource not found"})
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "status_code": "404 Not Found",
            "title": "Analysis Report Not Found",
            "message": "The diagnostic record you are looking for does not exist or has expired."
        },
        status_code=404
    )


@app.exception_handler(500)
async def custom_500_handler(request: Request, exc: Exception):
    """Custom 500 page styled with design tokens."""
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=500, content={"detail": "Internal server error occurred."})
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "status_code": "500 Server Error",
            "title": "Processing Error",
            "message": "An error occurred while compiling your report. Please retry your request."
        },
        status_code=500
    )


# Mount Static Files
static_dir = BASE_DIR / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Jinja2 Templates Engine
templates_dir = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """
    Renders the Resumely AI landing page, pixel-faithful to /design.
    """
    model_name_display = GEMINI_MODEL.replace("-", " ").title()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "criteria": SCORING_CRITERIA,
            "creator": CREATOR_INFO,
            "gemini_model_display": model_name_display,
            "max_file_size_mb": MAX_FILE_SIZE_MB
        }
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": "Resumely AI",
        "model": GEMINI_MODEL,
        "criteria_count": len(SCORING_CRITERIA)
    }


# ==========================================
# PHASE 2: EXTRACTION ROUTES
# ==========================================

@app.get("/test-extract", response_class=HTMLResponse)
async def test_extract_page(request: Request):
    """
    Renders the Phase 2 test harness for inspecting text extraction.
    """
    return templates.TemplateResponse(
        request=request,
        name="test_extract.html",
        context={"result": None, "error": None}
    )


@app.post("/test-extract", response_class=HTMLResponse)
async def handle_test_extract(request: Request, file: UploadFile = File(...)):
    """
    Handles file upload on the test route and displays extracted text & metrics.
    """
    error_msg = None
    extraction_result = None

    try:
        content = await file.read()
        if not content:
            raise ExtractionError("The uploaded file was empty.")

        extraction_result = process_resume_upload(
            file_bytes=content,
            original_filename=file.filename or "uploaded_resume.pdf"
        )
    except (ExtractionError, EmptyExtractionError) as e:
        error_msg = str(e)
    except Exception as e:
        error_msg = f"Unexpected processing error: {e}"

    return templates.TemplateResponse(
        request=request,
        name="test_extract.html",
        context={
            "result": extraction_result,
            "error": error_msg
        }
    )


@app.post("/api/extract")
async def api_extract_text(file: UploadFile = File(...)):
    """
    JSON API endpoint for text extraction.
    """
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        result = process_resume_upload(
            file_bytes=content,
            original_filename=file.filename or "resume.pdf"
        )
        return {
            "success": True,
            **result.to_dict()
        }
    except (ExtractionError, EmptyExtractionError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal extraction error: {e}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=HOST, port=PORT, reload=DEBUG)
