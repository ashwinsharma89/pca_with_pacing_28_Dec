"""
PCA Agent - Diagnostics-Only Streamlit App

Provides performance diagnostics (causal + driver + comprehensive analysis)
without the heavier main app features.

Run with:
    streamlit run streamlit_modular_v1.py --server.port 8503
"""

import os
import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Add project root to path
def _add_project_root_to_sys_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = current_dir
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


_add_project_root_to_sys_path()

# Load environment variables early
load_dotenv()

from src.ui.diagnostics_component import DiagnosticsComponent
from src.utils.data_validator import validate_and_clean_data
from src.agents.visualization_filters import SmartFilterEngine

# Paths
SAMPLE_DATA_PATH = Path(__file__).parent / "data" / "historical_campaigns_sample.csv"

# Page config
st.set_page_config(
    page_title="PCA Agent - Diagnostics",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Minimal CSS
def _inject_css():
    st.markdown(
        """
        <style>
            .main-header {
                font-size: 2.4rem;
                font-weight: 700;
                color: #5b6ef5;
                margin-bottom: 1rem;
            }
            .stSidebar .sidebar-title {
                font-size: 1.1rem;
                font-weight: 600;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


_inject_css()


def init_session_state():
    defaults = {
        "df": None,
        "validation_report": None,
        "df_source": None,
        "filter_engine": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar() -> str:
    st.sidebar.markdown("## 🎛️ Advanced Analytics Suite")
    st.sidebar.markdown("*Deep Dive • Visualizations • Diagnostics*")

    st.sidebar.info(
        """This dedicated app isolates the diagnostics tab
        to keep the main PCA Agent lightweight. Upload data here or
        use the sample dataset, then open the Diagnostics page."""
    )

    st.sidebar.divider()

    page = st.sidebar.radio(
        "Navigation",
        options=["Data Upload", "In-Depth Analysis", "Visualizations", "Diagnostics"],
        index=1 if st.session_state.df is not None else 0,
    )

    st.sidebar.divider()

    if st.session_state.df is not None:
        st.sidebar.success(
            f"✅ Data ready: {len(st.session_state.df):,} rows"
        )
        if st.sidebar.button("🗑️ Clear Data"):
            st.session_state.df = None
            st.session_state.validation_report = None
            st.session_state.df_source = None
            st.rerun()
    else:
        st.sidebar.warning("No data loaded")

    return page


def render_data_upload_page():
    st.markdown('<div class="main-header">📁 Data Upload</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=["csv"],
        help="Upload campaign performance data",
    )

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            _process_uploaded_df(df, source=f"File: {uploaded_file.name}")
        except Exception as exc:
            st.error(f"❌ Failed to read file: {exc}")

    st.divider()

    col1, col2 = st.columns([1, 2])
    with col1:
        if SAMPLE_DATA_PATH.exists():
            if st.button("📊 Load Sample Data"):
                sample_df = pd.read_csv(SAMPLE_DATA_PATH)
                _process_uploaded_df(sample_df, source="Sample Dataset")
        else:
            st.info("Sample dataset not found")

    with col2:
        st.caption("Sample file: data/historical_campaigns_sample.csv")

    if st.session_state.df is not None:
        _render_data_preview()


def _process_uploaded_df(df: pd.DataFrame, source: str):
    with st.spinner("🔍 Validating & cleaning data..."):
        try:
            cleaned_df, validation_report = validate_and_clean_data(df)
            st.session_state.df = cleaned_df
            st.session_state.validation_report = validation_report
            st.session_state.df_source = source
            st.success(
                f"✅ Data ready! {validation_report['summary']['cleaned_rows']} rows"
            )
        except Exception as exc:
            st.error(f"Validation error: {exc}")


def _render_data_preview():
    st.subheader("📋 Data Preview")
    st.caption(
        f"Source: {st.session_state.df_source or 'Unknown'}"
    )
    st.dataframe(
        st.session_state.df.head(15),
        use_container_width=True,
        height=350,
    )

    if st.session_state.validation_report:
        with st.expander("ℹ️ Validation Summary", expanded=False):
            summary = st.session_state.validation_report.get("summary", {})
            for key, value in summary.items():
                st.markdown(f"- **{key.replace('_', ' ').title()}**: {value}")


def render_deep_dive_page():
    st.markdown('<div class="main-header">🔍 In-Depth Analysis</div>', unsafe_allow_html=True)

    if st.session_state.df is None:
        st.warning("⚠️ Please upload data first")
        return

    df = st.session_state.df

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    st.markdown("### 🎨 Custom Chart Builder")
    st.markdown("*Build custom visualizations with your data*")

    col1, col2, col3 = st.columns(3)

    with col1:
        custom_chart_type = st.selectbox(
            "Chart Type",
            ["Bar Chart", "Line Chart", "Scatter Plot", "Area Chart", "Pie Chart", "Heatmap", "Box Plot"],
        )

    with col2:
        if custom_chart_type in ["Bar Chart", "Line Chart", "Area Chart"]:
            x_axis = st.selectbox("X-Axis", categorical_cols + (['Date'] if 'Date' in df.columns else []))
        elif custom_chart_type == "Scatter Plot":
            x_axis = st.selectbox("X-Axis (Numeric)", numeric_cols)
        elif custom_chart_type == "Pie Chart":
            x_axis = st.selectbox("Category", categorical_cols)
        else:
            x_axis = st.selectbox("X-Axis", categorical_cols)

    with col3:
        y_axis = st.selectbox("Y-Axis (Metric)", numeric_cols)

    col1, col2 = st.columns(2)
    with col1:
        color_by = st.selectbox("Color By (Optional)", ["None"] + categorical_cols)
    with col2:
        aggregation = st.selectbox("Aggregation", ["Sum", "Mean", "Count", "Max", "Min"])

    if st.button("📊 Generate Custom Chart"):
        _render_custom_chart(df, custom_chart_type, x_axis, y_axis, color_by, aggregation)

    st.divider()

    st.markdown("### 🎨 Custom Chart Builder-2")
    st.markdown("*Compare multiple KPIs side-by-side*")

    col1, col2 = st.columns(2)

    with col1:
        kpi_options = [col for col in numeric_cols if col in ['Spend', 'Clicks', 'Conversions', 'Impressions', 'Revenue', 'CPA', 'CPC', 'CTR', 'ROAS']]
        selected_kpis = st.multiselect(
            "Select KPIs to Compare",
            kpi_options,
            default=kpi_options[:3] if len(kpi_options) >= 3 else kpi_options,
        )

    with col2:
        dimension_options = ['Platform']
        if 'Campaign_Name' in df.columns:
            dimension_options.append('Campaign')
        if 'Placement' in df.columns:
            dimension_options.append('Placement')
        if 'Audience' in df.columns or 'Audience_Segment' in df.columns:
            dimension_options.append('Audience')
        compare_dimension = st.selectbox("Group By", dimension_options)

    col1, col2 = st.columns(2)
    with col1:
        chart_type_2 = st.selectbox("Chart Type", ["Grouped Bar", "Line", "Radar"], key="chart_type_2")
    with col2:
        normalize_data = st.checkbox("Normalize Data (0-100 scale)", value=False)

    if st.button("📊 Generate KPI Comparison", key="generate_kpi_comparison"):
        _render_kpi_comparison(df, selected_kpis, compare_dimension, chart_type_2, normalize_data)

    st.divider()

    st.markdown("### 🎯 Smart Filters")

    if st.session_state.filter_engine is None:
        try:
            st.session_state.filter_engine = SmartFilterEngine()
        except Exception:
            pass

    col1, col2, col3 = st.columns(3)

    with col1:
        platforms = ['All'] + sorted(df['Platform'].dropna().unique().tolist()) if 'Platform' in df.columns else ['All']
        selected_platform = st.selectbox("📱 Platform", platforms)

    with col2:
        if 'Date' in df.columns:
            try:
                df_dates = pd.to_datetime(df['Date'], format='mixed', dayfirst=True, errors='coerce')
                min_date = df_dates.min()
                max_date = df_dates.max()
                date_range = st.date_input(
                    "📅 Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date,
                )
            except Exception:
                date_range = None
        else:
            date_range = None

    with col3:
        metric_options = ['Spend', 'Clicks', 'Conversions', 'Impressions', 'Revenue']
        available_metrics = [m for m in metric_options if m in df.columns]
        selected_metric = st.selectbox("📊 Primary Metric", available_metrics) if available_metrics else None

    filtered_df = _apply_filters(df, selected_platform, date_range)

    st.markdown(f"### 📊 Filtered Results ({len(filtered_df)} rows)")
    _render_filtered_metrics(filtered_df)

    st.markdown("### 💰 Spend-Click Analysis by Dimension")
    _render_spend_click_analysis(filtered_df)

    with st.expander("📋 View Filtered Data"):
        st.dataframe(filtered_df, use_container_width=True, height=400)

    if st.button("💾 Export to CSV", key="deep_dive_export"):
        st.download_button(
            label="Download CSV",
            data=filtered_df.to_csv(index=False),
            file_name="filtered_data.csv",
            mime="text/csv",
        )


def render_visualizations_page():
    st.markdown('<div class="main-header">📈 Smart Visualizations</div>', unsafe_allow_html=True)

    if st.session_state.df is None:
        st.warning("⚠️ Please upload data first")
        return

    df = st.session_state.df

    viz_type = st.selectbox(
        "Select visualization",
        [
            "Performance Overview",
            "Trend Analysis",
            "Platform Comparison",
            "Funnel Analysis",
            "Correlation Matrix",
            "Custom Chart",
        ],
    )

    st.divider()

    with st.expander("🎯 Smart Filters", expanded=True):
        viz_filters = _render_visualization_filters(df)

    _render_visualization_content(df, viz_type, viz_filters)


def _render_custom_chart(df, chart_type, x_axis, y_axis, color_by, aggregation):
    agg_map = {"Sum": "sum", "Mean": "mean", "Count": "count", "Max": "max", "Min": "min"}

    try:
        if chart_type == "Bar Chart":
            chart_data = df.groupby(x_axis)[y_axis].agg(agg_map[aggregation]).reset_index()
            if color_by != "None":
                chart_data = df.groupby([x_axis, color_by])[y_axis].agg(agg_map[aggregation]).reset_index()
                fig = px.bar(chart_data, x=x_axis, y=y_axis, color=color_by, title=f"{y_axis} by {x_axis}")
            else:
                fig = px.bar(chart_data, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
        elif chart_type == "Line Chart":
            chart_data = df.groupby(x_axis)[y_axis].agg(agg_map[aggregation]).reset_index()
            fig = px.line(chart_data, x=x_axis, y=y_axis, title=f"{y_axis} Trend")
        elif chart_type == "Scatter Plot":
            fig = px.scatter(df, x=x_axis, y=y_axis, color=None if color_by == "None" else color_by, title=f"{y_axis} vs {x_axis}")
        elif chart_type == "Area Chart":
            chart_data = df.groupby(x_axis)[y_axis].agg(agg_map[aggregation]).reset_index()
            fig = px.area(chart_data, x=x_axis, y=y_axis, title=f"{y_axis} Area")
        elif chart_type == "Pie Chart":
            chart_data = df.groupby(x_axis)[y_axis].agg(agg_map[aggregation]).reset_index()
            fig = px.pie(chart_data, values=y_axis, names=x_axis, title=f"{y_axis} Distribution")
        elif chart_type == "Box Plot":
            fig = px.box(df, x=x_axis, y=y_axis, color=None if color_by == "None" else color_by, title=f"{y_axis} Distribution by {x_axis}")
        elif chart_type == "Heatmap":
            pivot_data = df.pivot_table(values=y_axis, index=x_axis, columns=None if color_by == "None" else color_by, aggfunc=agg_map[aggregation])
            fig = px.imshow(pivot_data, title=f"{y_axis} Heatmap", aspect="auto")
        else:
            st.warning("Unsupported chart type")
            return

        fig.update_layout(template='plotly_dark', height=500, margin=dict(l=60, r=40, t=60, b=60))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as exc:
        st.error(f"Error creating chart: {str(exc)[:200]}")


def _render_kpi_comparison(df, selected_kpis, compare_dimension, chart_type, normalize_data):
    if not selected_kpis or not compare_dimension:
        st.warning("Please select at least one KPI and a dimension")
        return

    dim_map = {
        'Platform': 'Platform',
        'Campaign': 'Campaign_Name',
        'Placement': 'Placement',
        'Audience': 'Audience' if 'Audience' in df.columns else 'Audience_Segment',
    }
    actual_dim = dim_map.get(compare_dimension, 'Platform')

    if actual_dim not in df.columns:
        st.warning(f"Column {actual_dim} not found in data")
        return

    try:
        agg_data = df.groupby(actual_dim)[selected_kpis].sum().reset_index()

        if normalize_data:
            for kpi in selected_kpis:
                max_val = agg_data[kpi].max()
                if max_val > 0:
                    agg_data[f"{kpi}_norm"] = (agg_data[kpi] / max_val) * 100
            value_cols = [f"{kpi}_norm" for kpi in selected_kpis]
        else:
            value_cols = selected_kpis

        melted = agg_data.melt(id_vars=[actual_dim], value_vars=value_cols, var_name='KPI', value_name='Value')

        if chart_type == "Grouped Bar":
            fig = px.bar(melted, x='KPI', y='Value', color=actual_dim, barmode='group', title=f"KPI Comparison by {compare_dimension}")
        elif chart_type == "Line":
            fig = px.line(melted, x='KPI', y='Value', color=actual_dim, markers=True, title=f"KPI Comparison by {compare_dimension}")
        elif chart_type == "Radar":
            fig = go.Figure()
            for dim_val in agg_data[actual_dim].unique():
                dim_data = melted[melted[actual_dim] == dim_val]
                fig.add_trace(go.Scatterpolar(r=dim_data['Value'], theta=dim_data['KPI'], fill='toself', name=str(dim_val)))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True)), title=f"KPI Radar: {compare_dimension}")
        else:
            st.warning("Unsupported chart type")
            return

        fig.update_layout(template='plotly_dark', height=500, margin=dict(l=60, r=40, t=60, b=60))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as exc:
        st.error(f"Error creating KPI comparison: {str(exc)[:200]}")


def _apply_filters(df, platform, date_range):
    filtered = df.copy()

    if platform != 'All' and 'Platform' in filtered.columns:
        filtered = filtered[filtered['Platform'] == platform]

    if date_range and 'Date' in filtered.columns and len(date_range) == 2:
        try:
            filtered['Date_parsed'] = pd.to_datetime(filtered['Date'], errors='coerce')
            filtered = filtered[(filtered['Date_parsed'] >= pd.to_datetime(date_range[0])) & (filtered['Date_parsed'] <= pd.to_datetime(date_range[1]))]
            filtered = filtered.drop(columns=['Date_parsed'])
        except Exception:
            pass

    return filtered


def _render_filtered_metrics(filtered_df):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if 'Spend' in filtered_df.columns:
            st.metric("Total Spend", f"${filtered_df['Spend'].sum():,.2f}")

    with col2:
        if 'Conversions' in filtered_df.columns:
            st.metric("Total Conversions", f"{filtered_df['Conversions'].sum():,.0f}")

    with col3:
        if 'Clicks' in filtered_df.columns:
            st.metric("Total Clicks", f"{filtered_df['Clicks'].sum():,.0f}")

    with col4:
        if 'Impressions' in filtered_df.columns:
            st.metric("Total Impressions", f"{filtered_df['Impressions'].sum():,.0f}")


def _render_spend_click_analysis(df):
    if 'Spend' not in df.columns or 'Clicks' not in df.columns:
        st.info("Spend and Clicks columns required for this analysis")
        return

    dimension_map = {}
    if 'Platform' in df.columns:
        dimension_map['Platform'] = 'Platform'

    for col in ['Campaign_Name', 'Placement', 'Audience', 'Audience_Segment', 'Source', 'Channel']:
        if col in df.columns:
            dimension_map[col] = col

    if not dimension_map:
        st.info("No additional dimensions available")
        return

    dim_label = st.selectbox("Select Dimension", list(dimension_map.keys()))
    actual_col = dimension_map[dim_label]

    try:
        analysis = df.groupby(actual_col).agg({'Spend': 'sum', 'Clicks': 'sum'}).reset_index()
        analysis['CPC'] = analysis['Spend'] / analysis['Clicks'].replace(0, float('nan'))

        fig = px.scatter(
            analysis,
            x='Spend',
            y='Clicks',
            size='Clicks',
            color=actual_col,
            text=actual_col,
            title=f"Spend vs Clicks by {dim_label}",
            hover_data={actual_col: True, 'Spend': ':,.0f', 'Clicks': ':,.0f', 'CPC': ':,.2f'},
        )
        fig.update_layout(template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            analysis.sort_values('Spend', ascending=False).style.format({'Spend': '${:,.2f}', 'Clicks': '{:,.0f}', 'CPC': '${:,.2f}'}),
            use_container_width=True,
        )
    except Exception as exc:
        st.error(f"Error creating spend-click analysis: {str(exc)[:200]}")


def _render_visualization_filters(df):
    filters = {}

    col1, col2, col3 = st.columns(3)
    with col1:
        platforms = ['All'] + sorted(df['Platform'].dropna().unique().tolist()) if 'Platform' in df.columns else ['All']
        filters['platform'] = st.selectbox("📱 Platform", platforms)

    with col2:
        if 'Campaign_Name' in df.columns:
            campaigns = ['All'] + sorted(df['Campaign_Name'].dropna().unique().tolist())[:20]
            filters['campaign'] = st.selectbox("📋 Campaign", campaigns)
        else:
            filters['campaign'] = 'All'

    with col3:
        if 'Date' in df.columns:
            df_dates = pd.to_datetime(df['Date'], errors='coerce')
            if not df_dates.isna().all():
                filters['date_range'] = st.date_input("📅 Date Range", value=(df_dates.min(), df_dates.max()))
            else:
                filters['date_range'] = None
        else:
            filters['date_range'] = None

    return filters


def _render_visualization_content(df, viz_type, filters):
    if viz_type == "Performance Overview":
        _render_performance_overview(df)
    elif viz_type == "Trend Analysis":
        _render_trend_analysis(df)
    elif viz_type == "Platform Comparison":
        _render_platform_comparison(df)
    elif viz_type == "Funnel Analysis":
        _render_funnel_analysis(df)
    elif viz_type == "Correlation Matrix":
        _render_correlation_matrix(df)
    elif viz_type == "Custom Chart":
        st.info("Use the In-Depth Analysis tab for advanced custom charts")


def _render_performance_overview(df):
    """Render performance overview with key metrics."""
    st.markdown("### 📊 Performance Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'Spend' in df.columns:
            st.metric("Total Spend", f"${df['Spend'].sum():,.2f}")
    
    with col2:
        if 'Clicks' in df.columns:
            st.metric("Total Clicks", f"{df['Clicks'].sum():,.0f}")
    
    with col3:
        if 'Conversions' in df.columns:
            st.metric("Total Conversions", f"{df['Conversions'].sum():,.0f}")
    
    with col4:
        if 'Impressions' in df.columns:
            st.metric("Total Impressions", f"{df['Impressions'].sum():,.0f}")
    
    # Platform breakdown
    if 'Platform' in df.columns and 'Spend' in df.columns:
        st.markdown("#### By Platform")
        platform_data = df.groupby('Platform')[['Spend', 'Clicks', 'Conversions']].sum().reset_index()
        fig = px.bar(platform_data, x='Platform', y='Spend', title="Spend by Platform")
        fig.update_layout(template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)


def _render_trend_analysis(df):
    """Render trend analysis over time."""
    st.markdown("### 📈 Trend Analysis")
    
    if 'Date' not in df.columns:
        st.warning("Date column required for trend analysis")
        return
    
    try:
        df_copy = df.copy()
        df_copy['Date'] = pd.to_datetime(df_copy['Date'], errors='coerce')
        df_copy = df_copy.dropna(subset=['Date'])
        
        if len(df_copy) == 0:
            st.warning("No valid dates found")
            return
        
        # Daily trends
        daily = df_copy.set_index('Date').resample('D')[['Spend', 'Clicks', 'Conversions']].sum().reset_index()
        
        fig = go.Figure()
        if 'Spend' in daily.columns:
            fig.add_trace(go.Scatter(x=daily['Date'], y=daily['Spend'], name='Spend', mode='lines+markers'))
        if 'Clicks' in daily.columns:
            fig.add_trace(go.Scatter(x=daily['Date'], y=daily['Clicks'], name='Clicks', mode='lines+markers', yaxis='y2'))
        
        fig.update_layout(
            title="Daily Trends",
            template='plotly_dark',
            yaxis=dict(title='Spend'),
            yaxis2=dict(title='Clicks', overlaying='y', side='right')
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error rendering trend analysis: {str(e)}")


def _render_platform_comparison(df):
    """Render platform comparison charts."""
    st.markdown("### 🔄 Platform Comparison")
    
    if 'Platform' not in df.columns:
        st.warning("Platform column required")
        return
    
    platform_data = df.groupby('Platform').agg({
        'Spend': 'sum',
        'Clicks': 'sum',
        'Conversions': 'sum',
        'Impressions': 'sum'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Spend' in platform_data.columns:
            fig = px.pie(platform_data, values='Spend', names='Platform', title='Spend Distribution')
            fig.update_layout(template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'Clicks' in platform_data.columns:
            fig = px.pie(platform_data, values='Clicks', names='Platform', title='Clicks Distribution')
            fig.update_layout(template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)


def _render_funnel_analysis(df):
    """Render marketing funnel visualization."""
    st.markdown("### 🔄 Marketing Funnel")
    
    funnel_metrics = []
    funnel_values = []
    
    if 'Impressions' in df.columns:
        funnel_metrics.append('Impressions')
        funnel_values.append(df['Impressions'].sum())
    
    if 'Clicks' in df.columns:
        funnel_metrics.append('Clicks')
        funnel_values.append(df['Clicks'].sum())
    
    if 'Conversions' in df.columns:
        funnel_metrics.append('Conversions')
        funnel_values.append(df['Conversions'].sum())
    
    if len(funnel_metrics) < 2:
        st.warning("Need at least 2 funnel metrics (Impressions, Clicks, Conversions)")
        return
    
    fig = go.Figure(go.Funnel(
        y=funnel_metrics,
        x=funnel_values,
        textinfo="value+percent initial",
        marker=dict(color=['#667eea', '#764ba2', '#f093fb'])
    ))
    fig.update_layout(title="Marketing Funnel", template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)


def _render_correlation_matrix(df):
    """Render correlation matrix heatmap."""
    st.markdown("### 🔗 Correlation Matrix")
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) < 2:
        st.warning("Need at least 2 numeric columns for correlation analysis")
        return
    
    # Select relevant metrics
    metric_cols = [col for col in numeric_cols if col in ['Spend', 'Clicks', 'Conversions', 'Impressions', 'CPC', 'CPA', 'CTR', 'ROAS']]
    
    if len(metric_cols) < 2:
        metric_cols = numeric_cols[:min(10, len(numeric_cols))]
    
    corr_matrix = df[metric_cols].corr()
    
    fig = px.imshow(
        corr_matrix,
        text_auto='.2f',
        aspect='auto',
        title='Metric Correlations',
        color_continuous_scale='RdBu_r',
        zmin=-1,
        zmax=1
    )
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)


def render_diagnostics_page():
    st.markdown('<div class="main-header">🔬 Performance Diagnostics</div>', unsafe_allow_html=True)

    if st.session_state.df is None:
        st.warning("⚠️ Please upload data in the Data Upload tab")
        return

    DiagnosticsComponent.render(st.session_state.df)


def main():
    init_session_state()
    page = render_sidebar()

    if page == "Data Upload":
        render_data_upload_page()
    elif page == "In-Depth Analysis":
        render_deep_dive_page()
    elif page == "Visualizations":
        render_visualizations_page()
    elif page == "Diagnostics":
        render_diagnostics_page()

    st.divider()
    st.caption(
        "PCA Agent Diagnostics Module · Run alongside streamlit_modular.py"
    )


if __name__ == "__main__":
    main()
