"""
Analytics Async Tasks
"""
from src.tasks.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="generate_campaign_report", bind=True)
def generate_campaign_report(self, campaign_data: dict, user_id: str = None):
    """
    Generate campaign report asynchronously
    
    Args:
        campaign_data: Campaign data as dict
        user_id: Optional user ID for tracking
    """
    try:
        logger.info(f"Starting report generation for user {user_id}")
        
        # Import here to avoid circular dependencies
        from src.analytics.media_analytics_expert import MediaAnalyticsExpert
        import pandas as pd
        
        # Convert to DataFrame
        df = pd.DataFrame(campaign_data)
        
        # Generate analysis
        analytics = MediaAnalyticsExpert()
        results = analytics.analyze_all(df, use_parallel=True)
        
        logger.info(f"Report generation complete for user {user_id}")
        return {
            "status": "success",
            "results": results,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=True)
        # Retry up to 3 times with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries), max_retries=3)


@celery_app.task(name="process_bulk_upload")
def process_bulk_upload(file_path: str, user_id: str):
    """
    Process bulk campaign upload
    
    Args:
        file_path: Path to uploaded file
        user_id: User ID
    """
    try:
        logger.info(f"Processing bulk upload: {file_path}")
        
        import pandas as pd
        
        # Read file
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
        
        # Validate and clean data
        from src.utils.data_validator import validate_and_clean_data
        df_clean = validate_and_clean_data(df)
        
        # Store in database or process further
        # ... your processing logic ...
        
        logger.info(f"Bulk upload processed: {len(df_clean)} rows")
        return {
            "status": "success",
            "rows_processed": len(df_clean),
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Bulk upload failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "user_id": user_id
        }


@celery_app.task(name="analyze_campaign_performance")
def analyze_campaign_performance(campaign_id: str):
    """
    Analyze specific campaign performance
    
    Args:
        campaign_id: Campaign ID to analyze
    """
    try:
        logger.info(f"Analyzing campaign: {campaign_id}")
        
        # Fetch campaign data
        # ... your data fetching logic ...
        
        # Perform analysis
        # ... your analysis logic ...
        
        logger.info(f"Campaign analysis complete: {campaign_id}")
        return {
            "status": "success",
            "campaign_id": campaign_id
        }
        
    except Exception as e:
        logger.error(f"Campaign analysis failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "campaign_id": campaign_id
        }
