"""
Pacing Reports API Endpoints.

Handles:
- Template upload and management
- Report generation
- Report download
- Scheduled report management
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from loguru import logger

from ...agents.pacing_report_agent import PacingReportAgent, AggregationLevel


router = APIRouter(prefix="/pacing-reports", tags=["Pacing Reports"])

# Initialize agent
pacing_agent = PacingReportAgent()


# Request/Response Models
class GenerateReportRequest(BaseModel):
    """Request model for report generation."""
    template_filename: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    aggregation: AggregationLevel = AggregationLevel.DAILY
    filters: Optional[Dict[str, Any]] = None
    output_filename: Optional[str] = None
    max_daily_rows: Optional[int] = Field(
        None, 
        description="Maximum daily rows to include. None=no limit (full data). Set to 10000 for faster generation."
    )


class ReportResponse(BaseModel):
    """Response model for report operations."""
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TemplateInfo(BaseModel):
    """Template information model."""
    filename: str
    uploaded_at: str
    size_bytes: int
    valid: bool


# Endpoints

@router.post("/upload-template", response_model=ReportResponse)
async def upload_template(
    file: UploadFile = File(..., description="Excel template file (.xlsx)")
):
    """
    Upload an Excel template for pacing reports.
    
    The template should contain:
    - "Daily Pacing" sheet
    - "Weekly Pacing" sheet
    """
    try:
        # Validate file type
        if not file.filename.endswith('.xlsx'):
            raise HTTPException(
                status_code=400,
                detail="Only .xlsx files are supported"
            )
        
        # Read file content
        content = await file.read()
        
        # Save template
        template_path = pacing_agent.save_template(content, file.filename)
        
        # Validate template
        validation = pacing_agent.validate_template(template_path)
        
        if not validation['valid']:
            # Remove invalid template
            template_path.unlink()
            raise HTTPException(
                status_code=400,
                detail=f"Invalid template: {validation['error']}"
            )
        
        logger.info(f"Template uploaded successfully: {file.filename}")
        
        return ReportResponse(
            success=True,
            message="Template uploaded and validated successfully",
            data={
                "filename": template_path.name,
                "path": str(template_path),
                "sheets": validation['sheets'],
                "size_bytes": len(content)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Template upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates", response_model=ReportResponse)
async def list_templates():
    """List all uploaded templates."""
    try:
        templates = []
        
        for template_file in pacing_agent.templates_dir.glob("*.xlsx"):
            # Skip temporary Excel files
            if template_file.name.startswith('~$'):
                continue
                
            stat = template_file.stat()
            
            # Don't validate during listing (too slow for large files)
            # Validation happens during upload instead
            templates.append({
                "filename": template_file.name,
                "uploaded_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "size_bytes": stat.st_size,
                "valid": True  # Assume valid since it was validated during upload
            })
        
        # Sort by upload time (newest first)
        templates.sort(key=lambda x: x['uploaded_at'], reverse=True)
        
        return ReportResponse(
            success=True,
            data={"templates": templates, "count": len(templates)}
        )
        
    except Exception as e:
        logger.exception(f"Failed to list templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{filename}/validate", response_model=ReportResponse)
async def validate_existing_template(filename: str):
    """Validate an already uploaded template."""
    try:
        template_path = pacing_agent.templates_dir / filename
        if not template_path.exists():
            raise HTTPException(status_code=404, detail=f"Template not found: {filename}")
            
        validation = pacing_agent.validate_template(template_path)
        
        return ReportResponse(
            success=True,
            data={
                "valid": validation['valid'],
                "detected_sheets": validation.get('detected_sheets'),
                "sheet_info": validation.get('sheet_info'),
                "warnings": validation.get('warnings'),
                "suggestions": validation.get('suggestions'),
                "message": validation.get('message')
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Template validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}", response_model=ReportResponse)
async def get_job_status(job_id: str):
    """Get the status and progress of a background report generation job."""
    status_info = pacing_agent.get_job_status(job_id)
    if not status_info:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    
    return ReportResponse(
        success=True,
        data=status_info
    )


@router.get("/jobs", response_model=ReportResponse)
async def list_jobs(limit: int = 20):
    """
    List all background jobs with their status for progress monitoring.
    
    - **limit**: Maximum number of jobs to return (default: 20)
    """
    jobs = pacing_agent.list_all_jobs(limit=limit)
    return ReportResponse(
        success=True,
        data={
            "jobs": jobs,
            "count": len(jobs)
        }
    )


@router.post("/jobs/{job_id}/cancel", response_model=ReportResponse)
async def cancel_job(job_id: str):
    """Request cancellation of a running job."""
    if pacing_agent.cancel_job(job_id):
        return ReportResponse(
            success=True,
            message=f"Job {job_id} cancellation requested"
        )
    raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")


@router.post("/cache/clear", response_model=ReportResponse)
async def clear_template_cache():
    """Clear the template validation cache."""
    pacing_agent.clear_template_cache()
    return ReportResponse(
        success=True,
        message="Template validation cache cleared"
    )


# Batch Generation
class BatchGenerateRequest(BaseModel):
    """Request model for batch report generation."""
    requests: List[GenerateReportRequest]


@router.post("/batch-generate", response_model=ReportResponse)
async def batch_generate(batch_request: BatchGenerateRequest, background_tasks: BackgroundTasks):
    """
    Generate multiple pacing reports in batch.
    
    Each report is started as a separate background job.
    Returns a list of job IDs for tracking.
    """
    job_ids = []
    errors = []
    
    for i, request in enumerate(batch_request.requests):
        try:
            job_id = str(uuid.uuid4())
            template_path = pacing_agent.templates_dir / request.template_filename
            
            if not template_path.exists():
                errors.append({"index": i, "error": f"Template not found: {request.template_filename}"})
                continue
            
            pacing_agent._update_job_status(job_id, "pending", 0, f"Batch job {i+1}/{len(batch_request.requests)}")
            
            background_tasks.add_task(
                pacing_agent.generate_report,
                template_path=template_path,
                start_date=request.start_date,
                end_date=request.end_date,
                aggregation=request.aggregation,
                filters=request.filters,
                output_filename=request.output_filename,
                job_id=job_id,
                max_daily_rows=request.max_daily_rows
            )
            
            job_ids.append({"index": i, "job_id": job_id, "template": request.template_filename})
            
        except Exception as e:
            errors.append({"index": i, "error": str(e)})
    
    return ReportResponse(
        success=len(job_ids) > 0,
        message=f"Started {len(job_ids)} report(s), {len(errors)} failed",
        data={
            "jobs": job_ids,
            "errors": errors if errors else None,
            "total_requested": len(batch_request.requests),
            "started": len(job_ids)
        }
    )


@router.post("/generate", response_model=ReportResponse)
async def generate_report(request: GenerateReportRequest, background_tasks: BackgroundTasks):
    """
    Generate a pacing report from template and campaign data.
    
    STABLE: Handles large files (100+ MB) with chunked processing and background execution.
    
    - **template_filename**: Name of uploaded template
    - **start_date**: Start date (YYYY-MM-DD), optional
    - **end_date**: End date (YYYY-MM-DD), optional
    - **aggregation**: daily, weekly, or monthly
    - **filters**: Additional filters (platform, campaign_id, etc.)
    """
    try:
        # Generate a unique job ID
        job_id = str(uuid.uuid4())
        
        logger.info(f"Accepted report generation request: template={request.template_filename}, job_id={job_id}")
        
        # Pre-check: Find template
        template_path = pacing_agent.templates_dir / request.template_filename
        
        if not template_path.exists():
            logger.error(f"Template not found: {request.template_filename}")
            raise HTTPException(
                status_code=404,
                detail=f"Template not found: {request.template_filename}"
            )
        
        # Initialize job status
        pacing_agent._update_job_status(job_id, "pending", 0, "Queued for background processing...")
        
        # Add generation to background tasks
        background_tasks.add_task(
            pacing_agent.generate_report,
            template_path=template_path,
            start_date=request.start_date,
            end_date=request.end_date,
            aggregation=request.aggregation,
            filters=request.filters,
            output_filename=request.output_filename,
            job_id=job_id,
            max_daily_rows=request.max_daily_rows
        )
        
        return ReportResponse(
            success=True,
            message="Report generation started in background",
            data={"job_id": job_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to start report generation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)[:200]}"
        )


@router.get("/reports", response_model=ReportResponse)
async def list_reports():
    """List all generated reports."""
    try:
        reports = []
        
        for report_file in pacing_agent.outputs_dir.glob("*.xlsx"):
            stat = report_file.stat()
            
            reports.append({
                "filename": report_file.name,
                "generated_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "size_bytes": stat.st_size,
                "path": str(report_file)
            })
        
        # Sort by generation time (newest first)
        reports.sort(key=lambda x: x['generated_at'], reverse=True)
        
        return ReportResponse(
            success=True,
            data={"reports": reports, "count": len(reports)}
        )
        
    except Exception as e:
        logger.exception(f"Failed to list reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{filename}")
async def download_report(filename: str):
    """
    Download a generated report.
    
    - **filename**: Name of the report file to download
    """
    try:
        report_path = pacing_agent.outputs_dir / filename
        
        if not report_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Report not found: {filename}"
            )
        
        # Create FileResponse with explicit CORS headers for Chrome compatibility
        response = FileResponse(
            path=str(report_path),
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Add CORS headers explicitly (required for Chrome cross-origin downloads)
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition, Content-Type, Content-Length"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Report download failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/templates/{filename}", response_model=ReportResponse)
async def delete_template(filename: str):
    """Delete an uploaded template."""
    try:
        template_path = pacing_agent.templates_dir / filename
        
        if not template_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Template not found: {filename}"
            )
        
        template_path.unlink()
        logger.info(f"Template deleted: {filename}")
        
        return ReportResponse(
            success=True,
            message=f"Template '{filename}' deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Template deletion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reports/{filename}", response_model=ReportResponse)
async def delete_report(filename: str):
    """Delete a generated report."""
    try:
        report_path = pacing_agent.outputs_dir / filename
        
        if not report_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Report not found: {filename}"
            )
        
        report_path.unlink()
        logger.info(f"Report deleted: {filename}")
        
        return ReportResponse(
            success=True,
            message=f"Report '{filename}' deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Report deletion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=ReportResponse)
async def health_check():
    """Health check endpoint."""
    return ReportResponse(
        success=True,
        message="Pacing Reports API is healthy",
        data={
            "templates_dir": str(pacing_agent.templates_dir),
            "outputs_dir": str(pacing_agent.outputs_dir),
            "templates_count": len(list(pacing_agent.templates_dir.glob("*.xlsx"))),
            "reports_count": len(list(pacing_agent.outputs_dir.glob("*.xlsx")))
        }
    )
