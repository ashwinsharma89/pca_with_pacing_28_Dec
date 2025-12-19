import reflex as rx
import pandas as pd
import numpy as np
import os
from typing import List, Dict, Any, Optional
from .auth import AuthState
from src.utils.data_validator import validate_and_clean_data

class DataState(AuthState):
    """State for handling data loading and processing."""
    
    # Exposed Metrics
    total_rows: int = 0
    total_spend: str = "$0.00"
    total_clicks: str = "0"
    total_conversions: str = "0"
    total_impressions: str = "0"
    columns: List[str] = []
    numeric_columns: List[str] = []
    
    # Data Preview & Schema
    data_preview: List[Dict[str, Any]] = []
    column_types: List[Dict[str, str]] = []
    
    # Validation info
    validation_summary: str = ""
    
    # Internal dataframe storage (not sent to client)
    _df: Optional[pd.DataFrame] = None
    _uploaded_file_bytes: Optional[bytes] = None

    # Caching
    CACHE_FILE: str = ".cache/last_upload.pkl"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Attempt to load cache on init? 
        # State init happens per user session start.
        # We can try loading here, or explicit call on_mount.
        # Let's add a clear method for loading.
        pass

    def load_from_cache(self):
        """Load data from local cache if available."""
        if os.path.exists(self.CACHE_FILE):
             try:
                 df = pd.read_pickle(self.CACHE_FILE)
                 self.log(f"Loaded cached data from {self.CACHE_FILE}")
                 self.process_dataframe(df, cache=False) # Don't re-cache on load
             except Exception as e:
                 print(f"Cache load failed: {e}")

    def process_dataframe(self, df: pd.DataFrame, cache: bool = True):
        """Validate and process the dataframe."""
        self.log(f"Processing dataframe with shape: {df.shape}")
        try:
            cleaned_df, report = validate_and_clean_data(df)
            self._df = cleaned_df
            
            # Cache the clean data
            if cache:
                os.makedirs(os.path.dirname(self.CACHE_FILE), exist_ok=True)
                cleaned_df.to_pickle(self.CACHE_FILE)

            self.log(f"Data validation complete. Cleaned rows: {len(cleaned_df)}")
            
            # Update metrics
            self.compute_metrics(cleaned_df)
            
            # Update Preview & Schema - 50 Rows
            preview_df = cleaned_df.head(50).fillna("") 
            self.data_preview = preview_df.to_dict('records')
            
            self.column_types = [
                {"name": getattr(col, "name", str(col)), "type": str(dtype)} 
                for col, dtype in cleaned_df.dtypes.items()
            ]

            self.validation_summary = f"Loaded {self.total_rows} rows. {report['summary']['cleaned_rows']} valid."
            
        except Exception as e:
            print(f"Error processing dataframe: {e}")
            return rx.window_alert(f"Validation error: {str(e)}")
            
    # Excel Multi-Sheet Handling
    sheet_names: List[str] = []
    is_multi_sheet: bool = False
    
    def load_sample_data(self):
        """Load the sample dataset."""
        self.log("Loading sample data...")
        try:
            import src
            root_path = self.get_project_root()
            # Try enhanced sample first, then fallback
            enhanced_csv = os.path.join(root_path, "data", "enhanced_sample.csv")
            sample_csv = os.path.join(root_path, "data", "historical_campaigns_sample.csv")
            
            target_csv = enhanced_csv if os.path.exists(enhanced_csv) else sample_csv
            
            if os.path.exists(target_csv):
                self.log(f"Loading data from {target_csv}")
                df = pd.read_csv(target_csv)
                self.process_dataframe(df)
            else:
                print(f"Sample data not found at {target_csv}")
                return rx.window_alert("Sample data file not found.")
                
        except Exception as e:
            print(f"Error loading sample data: {e}")
            return rx.window_alert(f"Error loading data: {str(e)}")

    async def handle_upload(self, files: List[rx.UploadFile]):
        """Handle file upload with Excel support and caching."""
        self.log(f"Handling file upload: {len(files)} files")
        for file in files:
            upload_data = await file.read()
            self._uploaded_file_bytes = upload_data # Store for sheet switching
            self.sheet_names = []
            self.is_multi_sheet = False
            
            from io import BytesIO
            try:
                # Check for Excel
                if file.filename.endswith(('.xls', '.xlsx')):
                    xls = pd.ExcelFile(BytesIO(upload_data))
                    sheets = xls.sheet_names
                    
                    if len(sheets) > 1:
                        self.sheet_names = sheets
                        self.is_multi_sheet = True
                        self.log(f"Multi-sheet Excel detected: {sheets}")
                        return # Stop processing, wait for user selection
                    else:
                        # Single sheet, load immediately
                        df = pd.read_excel(BytesIO(upload_data))
                        self.process_dataframe(df)
                else:
                    # Default to CSV
                    df = pd.read_csv(BytesIO(upload_data))
                    self.process_dataframe(df)
            except Exception as e:
                return rx.window_alert(f"Error parsing file: {str(e)}")

    def load_selected_sheet(self, sheet_name: str):
        """Load a specific sheet from the uploaded Excel file."""
        if not self._uploaded_file_bytes:
             return rx.window_alert("No file loaded.")
             
        from io import BytesIO
        try:
            df = pd.read_excel(BytesIO(self._uploaded_file_bytes), sheet_name=sheet_name)
            self.process_dataframe(df)
            # Reset multi-sheet flag after loading to hide selector (optional, or keep it to switch)
            # self.is_multi_sheet = False 
        except Exception as e:
            return rx.window_alert(f"Error loading sheet: {e}")

    def compute_metrics(self, df: pd.DataFrame):
        """Compute summary metrics from the dataframe."""
        if df is None:
            return
 
        self.total_rows = len(df)
        self.columns = df.columns.tolist()
        self.numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if 'Spend' in df.columns:
            self.total_spend = f"${df['Spend'].sum():,.2f}"
        
        if 'Clicks' in df.columns:
            self.total_clicks = f"{df['Clicks'].sum():,.0f}"
            
        if 'Conversions' in df.columns:
            self.total_conversions = f"{df['Conversions'].sum():,.0f}"
            
        if 'Impressions' in df.columns:
            self.total_impressions = f"{df['Impressions'].sum():,.0f}"
 

 
    def get_project_root(self):
        from pathlib import Path
        import os
        current = Path(os.getcwd())
        if (current / "src").exists():
            return str(current)
        if (current.parent / "src").exists():
            return str(current.parent)
        return "/Users/ashwin/Desktop/pca_agent"
 
    def clear_data(self):
        """Clear the current dataset."""
        self._df = None
        self._uploaded_file_bytes = None
        self.sheet_names = []
        self.is_multi_sheet = False
        self.total_rows = 0
        self.total_spend = "$0.00"
        self.total_clicks = "0"
        self.total_conversions = "0"
        self.total_impressions = "0"
        self.columns = []
        self.validation_summary = ""
