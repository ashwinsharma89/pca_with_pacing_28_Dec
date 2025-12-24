"""
Data loading and ingestion component.
Handles CSV, Excel, S3, Azure, GCS uploads.
"""

import os
import logging
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

import pandas as pd
import streamlit as st

from src.utils.data_loader import DataLoader, normalize_campaign_dataframe

logger = logging.getLogger(__name__)

# Constants
LAST_CSV_PATH = Path("./data/last_uploaded.csv")
SAMPLE_DATA_PATH = Path("./data/sample_campaign_data.csv")

REQUIRED_COLUMNS = [
    "Campaign_Name", "Platform", "Spend", "Impressions", "Clicks"
]


@st.cache_data(ttl=3600, show_spinner="Loading cached data...")
def load_cached_dataframe() -> Optional[pd.DataFrame]:
    """Load last uploaded dataframe from cache."""
    if LAST_CSV_PATH.exists():
        try:
            df = pd.read_csv(LAST_CSV_PATH)
            df = normalize_campaign_dataframe(df)
            logger.info(f"Loaded cached data: {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Failed to load cached data: {e}")
    return None


def validate_campaign_dataframe(df: pd.DataFrame) -> Dict[str, list]:
    """
    Validate essential columns and data quality.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        Dictionary with validation results
    """
    report = {
        "missing_required": [col for col in REQUIRED_COLUMNS if col not in df.columns],
        "empty_columns": [col for col in df.columns if df[col].isna().all()],
        "duplicate_rows": df.duplicated().sum()
    }
    return report


def process_campaign_dataframe(
    df: pd.DataFrame,
    metadata: Dict[str, Any]
) -> Tuple[pd.DataFrame, Dict[str, Any], Dict[str, Any]]:
    """
    Normalize, validate, and log metadata for a campaign dataframe.
    
    Args:
        df: Raw DataFrame
        metadata: Metadata dictionary
        
    Returns:
        Tuple of (processed_df, updated_metadata, validation_report)
    """
    # Normalize
    df = normalize_campaign_dataframe(df)
    
    # Update metadata
    metadata.update({
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist()
    })
    
    # Validate
    validation = validate_campaign_dataframe(df)
    
    # Log
    logger.info(f"Processed dataframe: {metadata['rows']} rows, {metadata['columns']} columns")
    if validation['missing_required']:
        logger.warning(f"Missing required columns: {validation['missing_required']}")
    
    return df, metadata, validation


def ingest_campaign_data(
    uploaded_file,
    source: str = "upload"
) -> Tuple[Optional[pd.DataFrame], Dict[str, Any], Dict[str, Any]]:
    """
    Centralized ingestion pipeline with logging and validation.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        source: Source identifier
        
    Returns:
        Tuple of (dataframe, metadata, validation_report)
    """
    metadata = {
        "source": source,
        "filename": uploaded_file.name if hasattr(uploaded_file, 'name') else "unknown",
        "timestamp": pd.Timestamp.now().isoformat()
    }
    
    try:
        # Read file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            raise ValueError(f"Unsupported file type: {uploaded_file.name}")
        
        return process_campaign_dataframe(df, metadata)
        
    except Exception as e:
        logger.error(f"Failed to ingest data: {e}")
        return None, metadata, {"error": str(e)}


def load_sample_campaign_data() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Load bundled sample dataset for demos.
    
    Returns:
        Tuple of (dataframe, error_message)
    """
    if not SAMPLE_DATA_PATH.exists():
        return None, "Sample dataset not found"
    
    try:
        df = pd.read_csv(SAMPLE_DATA_PATH)
        df = normalize_campaign_dataframe(df)
        logger.info(f"Loaded sample data: {len(df)} rows")
        return df, None
    except Exception as e:
        logger.error(f"Failed to load sample data: {e}")
        return None, str(e)


def save_dataframe_cache(df: pd.DataFrame) -> bool:
    """
    Save dataframe to cache file.
    
    Args:
        df: DataFrame to cache
        
    Returns:
        True if successful
    """
    try:
        LAST_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(LAST_CSV_PATH, index=False)
        logger.info(f"Saved dataframe to cache: {len(df)} rows")
        return True
    except Exception as e:
        logger.error(f"Failed to save cache: {e}")
        return False


class DataLoaderComponent:
    """Streamlit component for data loading UI."""
    
    @staticmethod
    def render_file_uploader():
        """Render file upload UI."""
        st.subheader("📁 Upload Campaign Data")
        
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload your campaign performance data"
        )
        
        if uploaded_file:
            with st.spinner("Processing file..."):
                df, metadata, validation = ingest_campaign_data(uploaded_file)
                
                if df is not None:
                    # Show success
                    st.success(f"✅ Loaded {metadata['rows']} rows • {metadata['columns']} columns")
                    
                    # Show validation warnings
                    if validation.get('missing_required'):
                        st.warning(f"⚠️ Missing columns: {', '.join(validation['missing_required'])}")
                    
                    # Save to cache
                    save_dataframe_cache(df)
                    
                    # Save to session state
                    st.session_state.df = df
                    st.session_state.df_loaded_from_cache = False
                    
                    return df
                else:
                    st.error(f"❌ Failed to load file: {validation.get('error', 'Unknown error')}")
        
        return None
    
    @staticmethod
    def render_sample_data_button():
        """Render sample data load button."""
        if st.button("📊 Load Sample Data", help="Load demo campaign data"):
            with st.spinner("Loading sample data..."):
                df, error = load_sample_campaign_data()
                
                if df is not None:
                    st.success(f"✅ Loaded sample data: {len(df)} rows")
                    st.session_state.df = df
                    st.session_state.df_loaded_from_cache = False
                    return df
                else:
                    st.error(f"❌ {error}")
        
        return None
    
    @staticmethod
    def render_cloud_storage_options():
        """Render cloud storage connection options."""
        st.subheader("☁️ Cloud Storage")
        
        storage_type = st.selectbox(
            "Select storage type",
            ["None", "AWS S3", "Azure Blob", "Google Cloud Storage"]
        )
        
        if storage_type == "AWS S3":
            return DataLoaderComponent._render_s3_loader()
        elif storage_type == "Azure Blob":
            return DataLoaderComponent._render_azure_loader()
        elif storage_type == "Google Cloud Storage":
            return DataLoaderComponent._render_gcs_loader()
        
        return None
    
    @staticmethod
    def _render_s3_loader():
        """Render S3 loader UI."""
        with st.expander("AWS S3 Configuration"):
            bucket = st.text_input("Bucket name")
            key = st.text_input("File key/path")
            region = st.text_input("Region", value="us-east-1")
            
            if st.button("Load from S3"):
                if bucket and key:
                    with st.spinner("Loading from S3..."):
                        try:
                            loader = DataLoader()
                            df = loader.load_from_s3(bucket, key, region_name=region)
                            df = normalize_campaign_dataframe(df)
                            
                            st.success(f"✅ Loaded {len(df)} rows from S3")
                            st.session_state.df = df
                            return df
                        except Exception as e:
                            st.error(f"❌ S3 load failed: {e}")
                else:
                    st.warning("Please provide bucket and key")
        
        return None
    
    @staticmethod
    def _render_azure_loader():
        """Render Azure Blob loader UI."""
        with st.expander("Azure Blob Configuration"):
            account_name = st.text_input("Account name")
            container = st.text_input("Container name")
            blob_name = st.text_input("Blob name")
            account_key = st.text_input("Account key", type="password")
            
            if st.button("Load from Azure"):
                if all([account_name, container, blob_name, account_key]):
                    with st.spinner("Loading from Azure..."):
                        try:
                            loader = DataLoader()
                            df = loader.load_from_azure(
                                account_name, container, blob_name, account_key
                            )
                            df = normalize_campaign_dataframe(df)
                            
                            st.success(f"✅ Loaded {len(df)} rows from Azure")
                            st.session_state.df = df
                            return df
                        except Exception as e:
                            st.error(f"❌ Azure load failed: {e}")
                else:
                    st.warning("Please provide all Azure credentials")
        
        return None
    
    @staticmethod
    def _render_gcs_loader():
        """Render GCS loader UI."""
        with st.expander("Google Cloud Storage Configuration"):
            bucket = st.text_input("Bucket name")
            blob_name = st.text_input("Blob name")
            credentials_path = st.text_input("Credentials JSON path (optional)")
            
            if st.button("Load from GCS"):
                if bucket and blob_name:
                    with st.spinner("Loading from GCS..."):
                        try:
                            loader = DataLoader()
                            df = loader.load_from_gcs(
                                bucket, blob_name,
                                credentials_path=credentials_path if credentials_path else None
                            )
                            df = normalize_campaign_dataframe(df)
                            
                            st.success(f"✅ Loaded {len(df)} rows from GCS")
                            st.session_state.df = df
                            return df
                        except Exception as e:
                            st.error(f"❌ GCS load failed: {e}")
                else:
                    st.warning("Please provide bucket and blob name")
        
        return None
