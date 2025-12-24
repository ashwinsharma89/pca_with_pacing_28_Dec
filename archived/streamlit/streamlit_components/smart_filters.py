"""
Interactive Filter UI Components for Streamlit
Provides user-friendly filter interface with smart suggestions
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, Any, Optional
from loguru import logger

from src.agents.visualization_filters import SmartFilterEngine, FilterType


class InteractiveFilterPanel:
    """Interactive filter panel for Streamlit UI"""
    
    def __init__(self, filter_engine: SmartFilterEngine, data: pd.DataFrame):
        """
        Initialize interactive filter panel
        
        Args:
            filter_engine: SmartFilterEngine instance
            data: Campaign data DataFrame
        """
        self.filter_engine = filter_engine
        self.data = data
        self.active_filters = {}
        logger.info("Initialized Interactive Filter Panel")
    
    def render(self, context: Optional[Dict] = None) -> pd.DataFrame:
        """
        Render interactive filter panel in Streamlit
        
        Args:
            context: Optional campaign context
        
        Returns:
            Filtered DataFrame
        """
        
        st.sidebar.header("🎛️ Smart Filters")
        
        # Get filter suggestions
        suggestions = self.filter_engine.suggest_filters_for_data(
            self.data,
            context or {}
        )
        
        logger.info(f"Rendering {len(suggestions)} filter suggestions")
        
        # Render each suggested filter
        for suggestion in suggestions:
            self._render_filter_widget(suggestion)
        
        # Add custom filter builder
        with st.sidebar.expander("➕ Add Custom Filter"):
            self._render_custom_filter_builder()
        
        # Show filter impact summary
        if self.active_filters:
            self._render_filter_summary()
        
        # Apply filters button
        if st.sidebar.button("🔄 Apply Filters", type="primary", use_container_width=True):
            filtered_data = self.filter_engine.apply_filters(
                self.data,
                self.active_filters
            )
            logger.info(f"Filters applied: {len(self.data)} → {len(filtered_data)} rows")
            return filtered_data
        
        return self.data
    
    def _render_filter_widget(self, suggestion: Dict):
        """Render appropriate widget based on filter type"""
        
        filter_type = suggestion['type']
        
        try:
            if filter_type == FilterType.DATE_PRESET:
                self._render_date_preset_filter(suggestion)
            
            elif filter_type == FilterType.CHANNEL:
                self._render_multiselect_filter(suggestion)
            
            elif filter_type == FilterType.PERFORMANCE_TIER:
                self._render_radio_filter(suggestion)
            
            elif filter_type == FilterType.METRIC_THRESHOLD:
                self._render_metric_threshold_filter(suggestion)
            
            elif filter_type == FilterType.BENCHMARK_RELATIVE:
                self._render_radio_filter(suggestion)
            
            elif filter_type == FilterType.DEVICE:
                self._render_multiselect_filter(suggestion)
            
            elif filter_type == FilterType.CAMPAIGN:
                self._render_multiselect_filter(suggestion)
            
            elif filter_type == FilterType.STATISTICAL:
                self._render_checkbox_filter(suggestion)
            
            elif filter_type == FilterType.ANOMALY:
                self._render_radio_filter(suggestion)
        
        except Exception as e:
            logger.error(f"Error rendering filter widget: {e}")
    
    def _render_date_preset_filter(self, suggestion: Dict):
        """Render date preset selector"""
        
        with st.sidebar.expander(f"📅 {suggestion['label']}", expanded=True):
            # Show reasoning
            st.caption(f"💡 {suggestion['reasoning']}")
            
            # Preset selection
            preset_options = suggestion['options']
            default_idx = (preset_options.index(suggestion['default']) 
                          if suggestion['default'] in preset_options else 0)
            
            preset = st.selectbox(
                "Select time period",
                options=preset_options,
                index=default_idx,
                key=f"filter_date_preset"
            )
            
            # Add option for custom date range
            use_custom = st.checkbox("Use custom date range", key="use_custom_date")
            
            if use_custom:
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input(
                        "Start",
                        value=datetime.now() - timedelta(days=30),
                        key="custom_start_date"
                    )
                with col2:
                    end_date = st.date_input(
                        "End",
                        value=datetime.now(),
                        key="custom_end_date"
                    )
                
                self.active_filters['date_range'] = {
                    'type': FilterType.DATE_RANGE,
                    'start_date': start_date,
                    'end_date': end_date
                }
            else:
                if preset != 'all':
                    self.active_filters['date_preset'] = {
                        'type': FilterType.DATE_PRESET,
                        'preset': preset
                    }
    
    def _render_multiselect_filter(self, suggestion: Dict):
        """Render multi-select filter"""
        
        with st.sidebar.expander(f"{suggestion['label']}"):
            st.caption(f"💡 {suggestion['reasoning']}")
            
            # Get options
            options = suggestion['options']
            default_selection = options if suggestion['default'] == 'all' else []
            
            selected = st.multiselect(
                f"Select {suggestion['label'].lower()}",
                options=options,
                default=default_selection,
                key=f"filter_{suggestion['label'].replace(' ', '_')}"
            )
            
            # Only add filter if selection differs from default
            if selected and selected != options:
                filter_key = suggestion['label'].lower().replace(' ', '_')
                self.active_filters[filter_key] = {
                    'type': suggestion['type'],
                    'column': suggestion.get('column', suggestion['type'].value),
                    'values': selected
                }
    
    def _render_radio_filter(self, suggestion: Dict):
        """Render radio button filter"""
        
        with st.sidebar.expander(f"{suggestion['label']}"):
            st.caption(f"💡 {suggestion['reasoning']}")
            
            # Format options for display
            if isinstance(suggestion['options'][0], dict):
                option_labels = [
                    f"{opt.get('icon', '')} {opt['label']}" 
                    for opt in suggestion['options']
                ]
                option_values = [opt['value'] for opt in suggestion['options']]
            else:
                option_labels = suggestion['options']
                option_values = suggestion['options']
            
            # Add "All" option
            option_labels = ['All'] + option_labels
            option_values = ['all'] + option_values
            
            selected_idx = st.radio(
                "Select option",
                range(len(option_labels)),
                format_func=lambda i: option_labels[i],
                key=f"filter_{suggestion['label'].replace(' ', '_')}"
            )
            
            selected_value = option_values[selected_idx]
            
            # Only add filter if not "All"
            if selected_value != 'all':
                filter_key = suggestion['label'].lower().replace(' ', '_')
                
                filter_config = {'type': suggestion['type']}
                
                if suggestion['type'] == FilterType.PERFORMANCE_TIER:
                    filter_config['tier'] = selected_value
                    filter_config['metric'] = suggestion.get('metric', 'conversions')
                elif suggestion['type'] == FilterType.BENCHMARK_RELATIVE:
                    filter_config['comparison'] = selected_value
                    filter_config['benchmarks'] = suggestion.get('benchmarks', {})
                elif suggestion['type'] == FilterType.ANOMALY:
                    filter_config['mode'] = selected_value
                    filter_config['metric'] = suggestion.get('metric', 'roas')
                
                self.active_filters[filter_key] = filter_config
    
    def _render_checkbox_filter(self, suggestion: Dict):
        """Render checkbox filter"""
        
        with st.sidebar.expander(f"{suggestion['label']}"):
            st.caption(f"💡 {suggestion['reasoning']}")
            
            # Format options
            if isinstance(suggestion['options'][0], dict):
                for opt in suggestion['options']:
                    checked = st.checkbox(
                        opt['label'],
                        key=f"filter_{suggestion['label']}_{opt['value']}"
                    )
                    
                    if checked and opt['value'] != 'all':
                        filter_key = suggestion['label'].lower().replace(' ', '_')
                        self.active_filters[filter_key] = {
                            'type': suggestion['type'],
                            'value': opt['value']
                        }
    
    def _render_metric_threshold_filter(self, suggestion: Dict):
        """Render metric threshold filter with sliders"""
        
        with st.sidebar.expander(f"📊 {suggestion['label']}"):
            st.caption(f"💡 {suggestion['reasoning']}")
            
            conditions = []
            
            for metric in suggestion['metrics']:
                st.markdown(f"**{metric.upper()}**")
                
                # Get min/max from data
                if metric in self.data.columns:
                    min_val = float(self.data[metric].min())
                    max_val = float(self.data[metric].max())
                    
                    # Enable filter checkbox
                    enable = st.checkbox(
                        f"Filter {metric}",
                        key=f"enable_{metric}"
                    )
                    
                    if enable:
                        # Operator selection
                        operator = st.selectbox(
                            "Condition",
                            options=['>', '>=', '<', '<=', 'between'],
                            key=f"operator_{metric}"
                        )
                        
                        # Value input
                        if operator == 'between':
                            range_vals = st.slider(
                                "Range",
                                min_value=min_val,
                                max_value=max_val,
                                value=(min_val, max_val),
                                key=f"range_{metric}"
                            )
                            value = range_vals
                        else:
                            value = st.number_input(
                                "Value",
                                min_value=min_val,
                                max_value=max_val,
                                value=(min_val + max_val) / 2,
                                key=f"value_{metric}"
                            )
                        
                        conditions.append({
                            'metric': metric,
                            'operator': operator,
                            'value': value
                        })
                    
                    st.markdown("---")
            
            if conditions:
                self.active_filters['metric_thresholds'] = {
                    'type': FilterType.METRIC_THRESHOLD,
                    'conditions': conditions
                }
    
    def _render_custom_filter_builder(self):
        """Allow users to build custom filters"""
        
        st.markdown("Build your own filter:")
        
        # Select column
        column = st.selectbox(
            "Column",
            options=self.data.columns.tolist(),
            key="custom_filter_column"
        )
        
        # Determine column type
        if pd.api.types.is_numeric_dtype(self.data[column]):
            # Numeric column
            operator = st.selectbox(
                "Operator",
                options=['>', '>=', '<', '<=', '==', '!=', 'between'],
                key="custom_filter_operator"
            )
            
            if operator == 'between':
                min_val = float(self.data[column].min())
                max_val = float(self.data[column].max())
                value = st.slider(
                    "Range",
                    min_value=min_val,
                    max_value=max_val,
                    value=(min_val, max_val),
                    key="custom_filter_value"
                )
            else:
                value = st.number_input(
                    "Value",
                    key="custom_filter_value"
                )
        else:
            # Categorical column
            operator = st.selectbox(
                "Operator",
                options=['equals', 'contains', 'in'],
                key="custom_filter_operator"
            )
            
            if operator == 'in':
                unique_vals = self.data[column].dropna().unique().tolist()
                value = st.multiselect(
                    "Values",
                    options=unique_vals,
                    key="custom_filter_value"
                )
            else:
                value = st.text_input(
                    "Value",
                    key="custom_filter_value"
                )
        
        if st.button("Add Custom Filter", key="add_custom_filter"):
            # Add custom filter
            custom_key = f"custom_{column}"
            
            if pd.api.types.is_numeric_dtype(self.data[column]):
                self.active_filters[custom_key] = {
                    'type': FilterType.METRIC_THRESHOLD,
                    'conditions': [{
                        'metric': column,
                        'operator': operator,
                        'value': value
                    }]
                }
            else:
                self.active_filters[custom_key] = {
                    'type': FilterType.CUSTOM,
                    'column': column,
                    'operator': operator,
                    'value': value
                }
            
            st.success(f"✅ Custom filter added for {column}")
    
    def _render_filter_summary(self):
        """Show impact of current filters"""
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Filter Impact")
        
        # Apply filters to get count
        try:
            filtered_data = self.filter_engine.apply_filters(
                self.data,
                self.active_filters
            )
            
            original_count = len(self.data)
            filtered_count = len(filtered_data)
            reduction_pct = (1 - filtered_count/original_count) * 100 if original_count > 0 else 0
            
            col1, col2 = st.sidebar.columns(2)
            col1.metric("Original", f"{original_count:,}")
            col2.metric("Filtered", f"{filtered_count:,}", f"-{reduction_pct:.1f}%")
            
            # Show active filters count
            st.sidebar.caption(f"🎛️ {len(self.active_filters)} active filter(s)")
            
            # Show warnings if any
            impact = self.filter_engine.get_filter_impact_summary()
            if impact.get('warnings'):
                for warning in impact['warnings']:
                    if warning['severity'] == 'high':
                        st.sidebar.error(f"⚠️ {warning['message']}")
                    elif warning['severity'] == 'medium':
                        st.sidebar.warning(f"⚡ {warning['message']}")
                    else:
                        st.sidebar.info(f"ℹ️ {warning['message']}")
        
        except Exception as e:
            logger.error(f"Error rendering filter summary: {e}")
            st.sidebar.error("Error calculating filter impact")
        
        # Clear filters button
        if st.sidebar.button("🗑️ Clear All Filters", use_container_width=True):
            self.active_filters = {}
            st.rerun()


class QuickFilterBar:
    """Quick filter bar for common filters (displayed in main area)"""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize quick filter bar
        
        Args:
            data: Campaign data DataFrame
        """
        self.data = data
        self.filters = {}
    
    def render(self) -> Dict:
        """
        Render quick filter bar
        
        Returns:
            Dictionary of active quick filters
        """
        
        st.markdown("### 🔍 Quick Filters")
        
        cols = st.columns(4)
        
        # Date range quick filter
        with cols[0]:
            date_preset = st.selectbox(
                "📅 Time Period",
                options=['All Time', 'Last 7 Days', 'Last 30 Days', 'Last 90 Days'],
                key="quick_date"
            )
            
            if date_preset != 'All Time':
                preset_map = {
                    'Last 7 Days': 'last_7_days',
                    'Last 30 Days': 'last_30_days',
                    'Last 90 Days': 'last_90_days'
                }
                self.filters['date'] = {
                    'type': FilterType.DATE_PRESET,
                    'preset': preset_map[date_preset]
                }
        
        # Channel quick filter
        with cols[1]:
            channel_col = self._get_column(['channel', 'platform'])
            if channel_col:
                channels = ['All'] + self.data[channel_col].dropna().unique().tolist()
                selected_channel = st.selectbox(
                    "📺 Channel",
                    options=channels,
                    key="quick_channel"
                )
                
                if selected_channel != 'All':
                    self.filters['channel'] = {
                        'type': FilterType.CHANNEL,
                        'column': channel_col,
                        'values': [selected_channel]
                    }
        
        # Device quick filter
        with cols[2]:
            device_col = self._get_column(['device', 'device_type'])
            if device_col:
                devices = ['All'] + self.data[device_col].dropna().unique().tolist()
                selected_device = st.selectbox(
                    "📱 Device",
                    options=devices,
                    key="quick_device"
                )
                
                if selected_device != 'All':
                    self.filters['device'] = {
                        'type': FilterType.DEVICE,
                        'column': device_col,
                        'values': [selected_device]
                    }
        
        # Performance tier quick filter
        with cols[3]:
            tier = st.selectbox(
                "⭐ Performance",
                options=['All', 'Top 20%', 'Middle 60%', 'Bottom 20%'],
                key="quick_tier"
            )
            
            if tier != 'All':
                tier_map = {
                    'Top 20%': 'top',
                    'Middle 60%': 'middle',
                    'Bottom 20%': 'bottom'
                }
                self.filters['tier'] = {
                    'type': FilterType.PERFORMANCE_TIER,
                    'tier': tier_map[tier],
                    'metric': 'roas'
                }
        
        return self.filters
    
    def _get_column(self, possible_names):
        """Find column from list of possible names"""
        data_cols_lower = {col.lower(): col for col in self.data.columns}
        
        for name in possible_names:
            if name.lower() in data_cols_lower:
                return data_cols_lower[name.lower()]
        
        return None


class FilterPresetsUI:
    """UI component for filter presets (uses comprehensive presets from filter_presets.py)"""
    
    @classmethod
    def render_preset_selector(cls, context: Optional[Dict] = None) -> Optional[Dict]:
        """
        Render preset selector with categories
        
        Args:
            context: Optional campaign context for recommendations
        
        Returns:
            Selected preset filters or None
        """
        
        from src.agents.filter_presets import FilterPresets
        
        st.markdown("### 🎯 Filter Presets")
        
        # Get categories
        categories = FilterPresets.get_categories()
        
        # Category selector
        selected_category = st.selectbox(
            "Category",
            options=['All Categories'] + categories,
            key="preset_category"
        )
        
        # Get presets for selected category
        if selected_category == 'All Categories':
            available_presets = FilterPresets.PRESETS
        else:
            available_presets = FilterPresets.get_presets_by_category(selected_category)
        
        # Preset selector
        preset_options = ['Custom'] + [
            f"{preset['name']}" 
            for preset in available_presets.values()
        ]
        
        selected = st.selectbox(
            "Select preset",
            options=preset_options,
            key="filter_preset"
        )
        
        if selected != 'Custom':
            # Find the preset
            for preset_key, preset_data in available_presets.items():
                if preset_data['name'] == selected:
                    # Show description and use case
                    st.info(f"📋 **{preset_data['description']}**\n\n💡 Use case: {preset_data['use_case']}")
                    
                    # Get full preset with context
                    full_preset = FilterPresets.get_preset(preset_key, context=context)
                    return full_preset['filters'] if full_preset else None
        
        return None
    
    @classmethod
    def render_recommended_presets(cls, context: Dict) -> Optional[Dict]:
        """
        Render recommended presets based on context
        
        Args:
            context: Campaign context
        
        Returns:
            Selected preset filters or None
        """
        
        from src.agents.filter_presets import FilterPresets
        
        st.markdown("### ⭐ Recommended Presets")
        st.caption("Based on your campaign context")
        
        # Get recommendations
        recommended = FilterPresets.get_recommended_presets(context)
        
        # Display as buttons
        cols = st.columns(min(len(recommended), 3))
        
        for idx, preset_name in enumerate(recommended[:3]):
            preset = FilterPresets.get_preset(preset_name, context=context)
            if preset:
                with cols[idx]:
                    if st.button(
                        preset['name'],
                        key=f"rec_preset_{preset_name}",
                        use_container_width=True
                    ):
                        st.info(f"📋 {preset['description']}")
                        return preset['filters']
        
        return None
