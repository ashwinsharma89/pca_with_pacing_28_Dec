"""
Report Generation Async Tasks
"""
from src.tasks.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="generate_pdf_report")
def generate_pdf_report(report_data: dict, user_id: str):
    """
    Generate PDF report asynchronously
    
    Args:
        report_data: Report data
        user_id: User ID
    """
    try:
        logger.info(f"Generating PDF report for user {user_id}")
        
        # Implement PDF generation logic here
        # You can use libraries like reportlab, weasyprint, etc.
        
        logger.info(f"PDF report generated for user {user_id}")
        return {
            "status": "success",
            "user_id": user_id,
            "report_path": f"reports/report_{user_id}.pdf"
        }
        
    except Exception as e:
        logger.error(f"PDF generation failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "user_id": user_id
        }


@celery_app.task(name="generate_excel_report")
def generate_excel_report(report_data: dict, user_id: str):
    """
    Generate Excel report asynchronously
    
    Args:
        report_data: Report data
        user_id: User ID
    """
    try:
        logger.info(f"Generating Excel report for user {user_id}")
        
        import pandas as pd
        
        # Convert report data to Excel
        df = pd.DataFrame(report_data)
        output_path = f"reports/report_{user_id}.xlsx"
        df.to_excel(output_path, index=False)
        
        logger.info(f"Excel report generated for user {user_id}")
        return {
            "status": "success",
            "user_id": user_id,
            "report_path": output_path
        }
        
    except Exception as e:
        logger.error(f"Excel generation failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "user_id": user_id
        }
