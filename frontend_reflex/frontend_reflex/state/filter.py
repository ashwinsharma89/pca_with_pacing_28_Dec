import reflex as rx
from typing import List, Optional
import pandas as pd
from datetime import datetime
from .data import DataState

class FilterState(DataState):
    """Mixin for Global Filters."""
    
    # Filter Selections
    filter_date_range: List[str] = [] # [start, end]
    selected_platforms: List[str] = []
    selected_campaigns: List[str] = []
    selected_audiences: List[str] = []
    selected_placements: List[str] = []
    selected_ad_types: List[str] = []
    selected_funnel_stages: List[str] = []
    
    # Filter Options
    available_platforms: List[str] = []
    available_campaigns: List[str] = []
    available_audiences: List[str] = []
    available_placements: List[str] = []
    available_ad_types: List[str] = []
    available_funnel_stages: List[str] = []
    
    @rx.var
    def platform_options(self) -> List[str]:
        return ["All Platforms"] + self.available_platforms

    @rx.var
    def audience_options(self) -> List[str]:
        return ["All Audiences"] + self.available_audiences

    @rx.var
    def placement_options(self) -> List[str]:
        return ["All Placements"] + self.available_placements

    @rx.var
    def ad_type_options(self) -> List[str]:
        return ["All Ad Types"] + self.available_ad_types

    @rx.var
    def funnel_options(self) -> List[str]:
         return ["All Stages"] + self.available_funnel_stages
    
    # ... (setters)

    def set_selected_ad_types(self, val: List[str]):
        if "All Ad Types" in val:
             self.selected_ad_types = []
        else:
             self.selected_ad_types = val
        self.apply_filters()
        
    # ...

    def update_filter_options(self):
        """Update available options based on data."""
        if self._df is not None:
             # Platforms
            if "Platform" in self._df.columns:
                self.available_platforms = sorted(self._df["Platform"].dropna().unique().tolist())
            
            # Campaigns
            if "Campaign" in self._df.columns:
                self.available_campaigns = sorted(self._df["Campaign"].dropna().unique().tolist())

            # Audiences
            if "Audience" in self._df.columns:
                self.available_audiences = sorted(self._df["Audience"].dropna().unique().tolist())
                
            # Placements
            if "Placement" in self._df.columns:
                self.available_placements = sorted(self._df["Placement"].dropna().unique().tolist())
            
            # Ad Types
            if "Ad Type" in self._df.columns:
                self.available_ad_types = sorted(self._df["Ad Type"].dropna().unique().tolist())
                
            # Funnel Stages (Dynamic or Static fallback)
            if "Funnel Stage" in self._df.columns:
                 self.available_funnel_stages = sorted(self._df["Funnel Stage"].dropna().unique().tolist())
            else:
                 self.available_funnel_stages = ["Awareness", "Consideration", "Conversion", "Loyalty"] # Fallback
            
            # ...

    # ...
    
    @property
    def filtered_df(self) -> pd.DataFrame:
        # ...
        
        # Filter by Ad Type
        if self.selected_ad_types:
             if "Ad Type" in df.columns:
                df = df[df["Ad Type"].isin(self.selected_ad_types)]
        
        # ...
    
    def set_date_range(self, dates: List[str]):
        self.filter_date_range = dates
        self.apply_filters()
        
    def set_start_date(self, date: str):
        if len(self.filter_date_range) == 2:
            self.filter_date_range = [date, self.filter_date_range[1]]
        else:
            self.filter_date_range = [date, date] # fallback
        self.apply_filters()

    def set_end_date(self, date: str):
        if len(self.filter_date_range) == 2:
             self.filter_date_range = [self.filter_date_range[0], date]
        else:
             self.filter_date_range = [date, date]
        self.apply_filters()
        
    def set_selected_platforms(self, platforms: List[str]):
        if "All Platforms" in platforms:
            self.selected_platforms = []
        else:
            self.selected_platforms = platforms
        self.apply_filters()
        
    def toggle_platform(self, platform: str, checked: bool):
        if checked:
            self.selected_platforms.append(platform)
        else:
            if platform in self.selected_platforms:
                self.selected_platforms.remove(platform)
        self.apply_filters()
        
    def set_selected_campaigns(self, campaigns: List[str]):
        self.selected_campaigns = campaigns
        self.apply_filters()

    def toggle_campaign(self, campaign: str, checked: bool):
        if checked:
            self.selected_campaigns.append(campaign)
        else:
            if campaign in self.selected_campaigns:
                self.selected_campaigns.remove(campaign)
        self.apply_filters()

    def set_selected_audiences(self, val: List[str]):
        if "All Audiences" in val:
            self.selected_audiences = []
        else:
            self.selected_audiences = val
        self.apply_filters()

    def set_selected_placements(self, val: List[str]):
        if "All Placements" in val:
            self.selected_placements = []
        else:
            self.selected_placements = val
        self.apply_filters()

    def set_selected_ad_types(self, val: List[str]):
        if "All Ad Types" in val:
             self.selected_ad_types = []
        else:
             self.selected_ad_types = val
        self.apply_filters()
        
    def set_selected_funnel_stages(self, val: List[str]):
        if "All Stages" in val:
             self.selected_funnel_stages = []
        else:
             self.selected_funnel_stages = val
        self.apply_filters()

    def update_filter_options(self):
        """Update available options based on data."""
        if self._df is not None:
             # Platforms
            if "Platform" in self._df.columns:
                self.available_platforms = sorted(self._df["Platform"].dropna().unique().tolist())
            
            # Campaigns
            if "Campaign" in self._df.columns:
                self.available_campaigns = sorted(self._df["Campaign"].dropna().unique().tolist())

            # Audiences
            if "Audience" in self._df.columns:
                self.available_audiences = sorted(self._df["Audience"].dropna().unique().tolist())
                
            # Placements
            if "Placement" in self._df.columns:
                self.available_placements = sorted(self._df["Placement"].dropna().unique().tolist())
            
            # Ad Types
            if "Ad Type" in self._df.columns:
                self.available_ad_types = sorted(self._df["Ad Type"].dropna().unique().tolist())
                
            # Funnel Stages (Dynamic or Static fallback)
            if "Funnel Stage" in self._df.columns:
                 self.available_funnel_stages = sorted(self._df["Funnel Stage"].dropna().unique().tolist())
            else:
                 self.available_funnel_stages = ["Awareness", "Consideration", "Conversion", "Loyalty"] # Fallback
            
            # Date Range default
            if not self.filter_date_range and self._df is not None:
                date_col = next((c for c in self._df.columns if 'date' in c.lower()), None)
                if date_col:
                     # Convert to datetime to find min/max
                     dates = pd.to_datetime(self._df[date_col], errors='coerce')
                     if not dates.empty:
                         self.filter_date_range = [
                             dates.min().strftime('%Y-%m-%d'),
                             dates.max().strftime('%Y-%m-%d')
                         ]

    def process_dataframe(self, df: pd.DataFrame):
        """Override to update options after processing."""
        super().process_dataframe(df)
        self.update_filter_options()

    def apply_filters(self):
        """Apply filters and update metrics."""
        df = self.filtered_df
        if df is not None:
            self.compute_metrics(df)

    @property
    def filtered_df(self) -> pd.DataFrame:
        """Return the dataframe filtered by current selections."""
        if self._df is None:
            return None
            
        df = self._df.copy()
        
        # Filter by Platform
        if self.selected_platforms:
            if "Platform" in df.columns:
                df = df[df["Platform"].isin(self.selected_platforms)]
                
        # Filter by Campaign
        if self.selected_campaigns:
            if "Campaign" in df.columns:
                df = df[df["Campaign"].isin(self.selected_campaigns)]

        # Filter by Audience
        if self.selected_audiences:
            if "Audience" in df.columns:
                df = df[df["Audience"].isin(self.selected_audiences)]

        # Filter by Placement
        if self.selected_placements:
             if "Placement" in df.columns:
                df = df[df["Placement"].isin(self.selected_placements)]

        # Filter by Ad Type
        if self.selected_ad_types:
             if "Ad Type" in df.columns:
                df = df[df["Ad Type"].isin(self.selected_ad_types)]
        
        # Filter by Funnel Stage
        if self.selected_funnel_stages:
             if "Funnel Stage" in df.columns:
                df = df[df["Funnel Stage"].isin(self.selected_funnel_stages)]
        
        # Filter by Date
        if self.filter_date_range and len(self.filter_date_range) == 2:
            date_col = next((c for c in df.columns if 'date' in c.lower()), None)
            if date_col:
                start_date = pd.to_datetime(self.filter_date_range[0])
                end_date = pd.to_datetime(self.filter_date_range[1])
                mask = (pd.to_datetime(df[date_col]) >= start_date) & (pd.to_datetime(df[date_col]) <= end_date)
                df = df.loc[mask]
                
        return df
