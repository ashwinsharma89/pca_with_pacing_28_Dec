import reflex as rx
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import List, Any, Dict, Optional
from .analysis import AnalysisState

class VizState(AnalysisState):
    """State for Visualizations and Deep Dive charts."""
    
    # Custom Chart Controls - Builder 1
    chart_type: str = "Bar Chart"
    x_axis: str = ""
    y_axis: str = ""
    color_by: str = "None"
    aggregation: str = "Sum"
    
    # Custom Chart Controls - Builder 2
    chart_type_2: str = "Bar Chart"
    x_axis_2: str = ""
    y_axis_2: str = ""
    color_by_2: str = "None"
    aggregation_2: str = "Sum"
    
    # Generated Chart
    custom_chart_figure: Optional[go.Figure] = None
    custom_chart_figure_2: Optional[go.Figure] = None
    
    # Pre-defined Charts
    funnel_figure: Optional[go.Figure] = None
    correlation_figure: Optional[go.Figure] = None
    
    # KPI Comparison Controls
    selected_kpis: List[str] = []
    primary_kpi: str = "Spend"
    compare_dimension: str = "Platform"
    comparison_chart_type: str = "Grouped Bar"
    normalize: bool = False
    comparison_chart_figure: Optional[go.Figure] = None

    @rx.var
    def color_options(self) -> List[str]:
        return self.columns + ["None"]

    def set_primary_kpi(self, value: str):
        self.primary_kpi = value
    
    def set_color_by(self, value: str):
        self.color_by = value

    def set_chart_type(self, value: str):
        self.chart_type = value

    def set_normalize(self, value: bool):
        self.normalize = value

    def update_x_axis(self, value: str):
        self.x_axis = value
        
    def update_y_axis(self, value: str):
        self.y_axis = value

    def set_aggregation(self, value: str):
        self.aggregation = value

    # Builder 2 Handlers
    def set_chart_type_2(self, value: str):
        self.chart_type_2 = value
        
    def update_x_axis_2(self, value: str):
        self.x_axis_2 = value
        
    def update_y_axis_2(self, value: str):
        self.y_axis_2 = value
        
    def set_color_by_2(self, value: str):
        self.color_by_2 = value
        
    def set_aggregation_2(self, value: str):
        self.aggregation_2 = value

    def set_compare_dimension(self, value: str):
        self.compare_dimension = value
        
    def toggle_kpi(self, kpi: str, checked: bool):
        if checked:
            if len(self.selected_kpis) >= 3:
                return rx.window_alert("Max 3 KPIs allowed.")
            self.selected_kpis.append(kpi)
        else:
            if kpi in self.selected_kpis:
                self.selected_kpis.remove(kpi)

    # Smart Chart Generator
    def _get_smart_chart_generator(self):
        try:
             from src.agents.chart_generators import SmartChartGenerator
             return SmartChartGenerator()
        except ImportError:
             print("SmartChartGenerator not found.")
             return None

    def generate_custom_chart(self):
        """Generate the custom chart based on selections (Builder 1)."""
        self._generate_custom_chart_internal(
            self.chart_type, self.x_axis, self.y_axis, 
            self.color_by, self.aggregation, target=1
        )

    def generate_custom_chart_2(self):
        """Generate the custom chart based on selections (Builder 2)."""
        self._generate_custom_chart_internal(
            self.chart_type_2, self.x_axis_2, self.y_axis_2, 
            self.color_by_2, self.aggregation_2, target=2
        )

    def _generate_custom_chart_internal(self, c_type, x_val, y_val, color_val, agg_val, target=1):
        """Internal shared method for chart generation."""
        df = self.filtered_df
        if df is None or df.empty:
            return
            
        if not x_val or not y_val:
            return
            
        agg_map = {"Sum": "sum", "Mean": "mean", "Count": "count", "Max": "max", "Min": "min"}
        
        try:
            # Fallback to manual plotly if simple chart
            if c_type == "Bar Chart":
                chart_data = df.groupby(x_val)[y_val].agg(agg_map[agg_val]).reset_index()
                if color_val != "None":
                    chart_data = df.groupby([x_val, color_val])[y_val].agg(agg_map[agg_val]).reset_index()
                    fig = px.bar(chart_data, x=x_val, y=y_val, color=color_val)
                else:
                    fig = px.bar(chart_data, x=x_val, y=y_val)
            
            elif c_type == "Line Chart":
                chart_data = df.groupby(x_val)[y_val].agg(agg_map[agg_val]).reset_index()
                fig = px.line(chart_data, x=x_val, y=y_val)
                
            elif c_type == "Scatter Plot":
                fig = px.scatter(df, x=x_val, y=y_val, 
                               color=color_val if color_val != "None" else None)
                               
            elif c_type == "Pie Chart":
                chart_data = df.groupby(x_val)[y_val].agg(agg_map[agg_val]).reset_index()
                fig = px.pie(chart_data, values=y_val, names=x_val)

            elif c_type == "Box Plot":
                fig = px.box(df, x=x_val, y=y_val,
                             color=color_val if color_val != "None" else None)

            elif c_type == "Area Chart":
                chart_data = df.groupby(x_val)[y_val].agg(agg_map[agg_val]).reset_index()
                fig = px.area(chart_data, x=x_val, y=y_val)

            elif c_type == "Heatmap":
                if color_val != "None":
                    pivot_data = df.pivot_table(
                        values=y_val, 
                        index=x_val, 
                        columns=color_val, 
                        aggfunc=agg_map[agg_val]
                    )
                    fig = px.imshow(pivot_data, text_auto=True, aspect="auto")
                else:
                    rx.window_alert("Heatmap requires 'Color By' to be set as the second dimension.")
                    return
            
            else:
                chart_data = df.groupby(x_val)[y_val].sum().reset_index()
                fig = px.bar(chart_data, x=x_val, y=y_val)
                
            fig.update_layout(title=f"Custom Chart {target}", template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            
            if target == 1:
                self.custom_chart_figure = fig
            else:
                self.custom_chart_figure_2 = fig
            
        except Exception as e:
            self.log(f"Chart gen error {target}: {e}", level="error")
            return rx.window_alert(f"Chart Error: {e}")

    def generate_funnel_chart(self):
        """Generate a funnel chart using SmartChartGenerator."""
        df = self.filtered_df
        if df is None or df.empty:
            return

        try:
            # Aggregate metrics for Smart Chart
            metrics = ['Impressions', 'Clicks', 'Conversions']
            values = []
            for m in metrics:
                if m in df.columns:
                    values.append(float(df[m].sum()))
                else:
                    values.append(0.0)
            
            generator = self._get_smart_chart_generator()
            if generator:
                funnel_data = {
                    'stages': metrics,
                    'values': values
                }
                fig = generator.create_conversion_funnel(funnel_data)
                # Ensure transparent background
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                self.funnel_figure = fig
            else:
                 # Fallback
                 fig = go.Figure(go.Funnel(
                    y=metrics,
                    x=values,
                    textinfo="value+percent initial"
                 ))
                 fig.update_layout(title="Conversion Funnel (Basic)", template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                 self.funnel_figure = fig
            
        except Exception as e:
            self.log(f"Funnel error: {e}", level="error")

    def generate_correlation_matrix(self):
        """Generate correlation matrix."""
        df = self.filtered_df
        if df is None or df.empty:
            return

        try:
            # Select numeric columns
            numeric_df = df.select_dtypes(include=[np.number])
            if numeric_df.empty:
                return
                
            corr = numeric_df.corr()
            
            fig = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r')
            fig.update_layout(title="Correlation Matrix", template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            self.correlation_figure = fig
            
        except Exception as e:
            self.log(f"Correlation error: {e}", level="error")

    def set_comparison_chart_type(self, value: str):
        self.comparison_chart_type = value

    def generate_comparison_chart(self):
        """Generate scale-adjusted comparison."""
        df = self.filtered_df
        if df is None or not self.selected_kpis:
            return

        try:
            # Group by dimension
            grouped = df.groupby(self.compare_dimension)[self.selected_kpis].sum().reset_index()
            
            # Normalize if requested
            chart_data = grouped.copy()
            if self.normalize:
                for kpi in self.selected_kpis:
                    max_val = chart_data[kpi].max()
                    if max_val > 0:
                        chart_data[kpi] = (chart_data[kpi] / max_val) * 100
            
            if self.comparison_chart_type == "Grouped Bar":
                 # Use melt for easier plotly express or go
                 melted = chart_data.melt(id_vars=[self.compare_dimension], value_vars=self.selected_kpis, var_name='KPI', value_name='Value')
                 fig = px.bar(melted, x='KPI', y='Value', color=self.compare_dimension, barmode='group')
            
            elif self.comparison_chart_type == "Line":
                 melted = chart_data.melt(id_vars=[self.compare_dimension], value_vars=self.selected_kpis, var_name='KPI', value_name='Value')
                 fig = px.line(melted, x='KPI', y='Value', color=self.compare_dimension, markers=True)

            elif self.comparison_chart_type == "Radar":
                 fig = go.Figure()
                 # Normalize for Radar if not already? Usually radar needs similar scales.
                 # If not normalized, radar might look weird if scales differ vastly.
                 for _, row in chart_data.iterrows():
                     fig.add_trace(go.Scatterpolar(
                         r=row[self.selected_kpis].values,
                         theta=self.selected_kpis,
                         fill='toself',
                         name=str(row[self.compare_dimension])
                     ))
                 fig.update_layout(polar=dict(radialaxis=dict(visible=True)))

            elif self.comparison_chart_type == "Dual Axis":
                if len(self.selected_kpis) < 2:
                    return rx.window_alert("Dual Axis requires at least 2 KPIs.")
                
                primary_kpi = self.selected_kpis[0]
                secondary_kpi = self.selected_kpis[1]
                
                fig = go.Figure()
                
                # Primary Axis (Bar)
                fig.add_trace(go.Bar(
                    x=chart_data[self.compare_dimension],
                    y=chart_data[primary_kpi],
                    name=primary_kpi,
                    yaxis='y',
                    offsetgroup=1
                ))
                
                # Secondary Axis (Line)
                fig.add_trace(go.Scatter(
                    x=chart_data[self.compare_dimension],
                    y=chart_data[secondary_kpi],
                    name=secondary_kpi,
                    yaxis='y2',
                    mode='lines+markers'
                ))
                
                fig.update_layout(
                    yaxis=dict(title=primary_kpi),
                    yaxis2=dict(
                        title=secondary_kpi,
                        overlaying='y',
                        side='right'
                    ),
                    legend=dict(x=0.1, y=1.1, orientation='h')
                )

            else:
                 # Fallback to Smart Chart (Grouped Bar)
                 # Revert to original logic if needed, but the simple melt above is robust
                 melted = chart_data.melt(id_vars=[self.compare_dimension], value_vars=self.selected_kpis, var_name='KPI', value_name='Value')
                 fig = px.bar(melted, x='KPI', y='Value', color=self.compare_dimension, barmode='group')

            title_prefix = "Normalized " if self.normalize else ""
            fig.update_layout(
                title=f"{title_prefix}Comparison by {self.compare_dimension}",
                template='plotly_dark', 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)'
            )
            self.comparison_chart_figure = fig
            
        except Exception as e:
            self.log(f"Comparison error: {e}", level="error")
            # print(f"DEBUG: Comparison error details: {e}")
