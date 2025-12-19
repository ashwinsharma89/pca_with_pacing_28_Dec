# NEW OPTIMIZED VERSION OF render_deep_dive_page()
# This will replace the existing function in streamlit_modular.py

def render_deep_dive_page():
    """Render in-depth analysis page with smart filters and custom chart builders."""
    st.markdown('<div class="main-header">🔍 In-Depth Analysis</div>', unsafe_allow_html=True)
    
    if st.session_state.df is None:
        st.warning("⚠️ Please upload data first")
        return
    
    df = st.session_state.df
    
    # ========================================
    # SECTION 1: CUSTOM CHART BUILDER (MOVED TO TOP, ALWAYS OPEN)
    # ========================================
    st.markdown("### 🎨 Custom Chart Builder")
    st.markdown("*Build custom visualizations with your data*")
    
    col1, col2, col3 = st.columns(3)
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    with col1:
        custom_chart_type = st.selectbox(
            "Chart Type",
            ["Bar Chart", "Line Chart", "Scatter Plot", "Area Chart", "Pie Chart", "Heatmap", "Box Plot"],
            key="custom_chart_type"
        )
    
    with col2:
        if custom_chart_type in ["Bar Chart", "Line Chart", "Area Chart"]:
            x_axis = st.selectbox("X-Axis", categorical_cols + (['Date'] if 'Date' in df.columns else []), key="custom_x")
        elif custom_chart_type == "Scatter Plot":
            x_axis = st.selectbox("X-Axis (Numeric)", numeric_cols, key="custom_x")
        elif custom_chart_type == "Pie Chart":
            x_axis = st.selectbox("Category", categorical_cols, key="custom_x")
        else:
            x_axis = st.selectbox("X-Axis", categorical_cols, key="custom_x")
    
    with col3:
        y_axis = st.selectbox("Y-Axis (Metric)", numeric_cols, key="custom_y")
    
    # Additional options
    col1, col2 = st.columns(2)
    with col1:
        color_by = st.selectbox("Color By (Optional)", ["None"] + categorical_cols, key="custom_color")
    with col2:
        aggregation = st.selectbox("Aggregation", ["Sum", "Mean", "Count", "Max", "Min"], key="custom_agg")
    
    if st.button("📊 Generate Custom Chart", key="generate_custom"):
        try:
            # Prepare data based on aggregation
            agg_map = {"Sum": "sum", "Mean": "mean", "Count": "count", "Max": "max", "Min": "min"}
            
            if custom_chart_type == "Bar Chart":
                chart_data = df.groupby(x_axis)[y_axis].agg(agg_map[aggregation]).reset_index()
                if color_by != "None":
                    chart_data = df.groupby([x_axis, color_by])[y_axis].agg(agg_map[aggregation]).reset_index()
                    fig = px.bar(chart_data, x=x_axis, y=y_axis, color=color_by, title=f"{y_axis} by {x_axis}")
                else:
                    fig = px.bar(chart_data, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
            
            elif custom_chart_type == "Line Chart":
                chart_data = df.groupby(x_axis)[y_axis].agg(agg_map[aggregation]).reset_index()
                fig = px.line(chart_data, x=x_axis, y=y_axis, title=f"{y_axis} Trend")
            
            elif custom_chart_type == "Scatter Plot":
                fig = px.scatter(df, x=x_axis, y=y_axis, 
                                color=color_by if color_by != "None" else None,
                                title=f"{y_axis} vs {x_axis}")
            
            elif custom_chart_type == "Area Chart":
                chart_data = df.groupby(x_axis)[y_axis].agg(agg_map[aggregation]).reset_index()
                fig = px.area(chart_data, x=x_axis, y=y_axis, title=f"{y_axis} Area")
            
            elif custom_chart_type == "Pie Chart":
                chart_data = df.groupby(x_axis)[y_axis].agg(agg_map[aggregation]).reset_index()
                fig = px.pie(chart_data, values=y_axis, names=x_axis, title=f"{y_axis} Distribution")
            
            elif custom_chart_type == "Box Plot":
                fig = px.box(df, x=x_axis, y=y_axis, 
                            color=color_by if color_by != "None" else None,
                            title=f"{y_axis} Distribution by {x_axis}")
            
            elif custom_chart_type == "Heatmap":
                pivot_data = df.pivot_table(values=y_axis, index=x_axis, 
                                            columns=color_by if color_by != "None" else None,
                                            aggfunc=agg_map[aggregation])
                fig = px.imshow(pivot_data, title=f"{y_axis} Heatmap", aspect="auto")
            
            fig.update_layout(template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating chart: {str(e)[:200]}")
    
    st.divider()
    
    # ========================================
    # SECTION 2: CUSTOM CHART BUILDER-2 (NEW - KPIs ON X-AXIS)
    # ========================================
    st.markdown("### 🎨 Custom Chart Builder-2")
    st.markdown("*Compare multiple KPIs side-by-side*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Select multiple KPIs for X-axis
        kpi_options = [col for col in numeric_cols if col in ['Spend', 'Clicks', 'Conversions', 'Impressions', 'Revenue', 'CPA', 'CPC', 'CTR', 'ROAS']]
        selected_kpis = st.multiselect(
            "Select KPIs to Compare",
            kpi_options,
            default=kpi_options[:3] if len(kpi_options) >= 3 else kpi_options,
            key="kpi_multiselect"
        )
    
    with col2:
        # Select dimension for grouping
        dimension_options = ['Platform']
        if 'Campaign_Name' in df.columns:
            dimension_options.append('Campaign')
        if 'Placement' in df.columns:
            dimension_options.append('Placement')
        if 'Audience' in df.columns or 'Audience_Segment' in df.columns:
            dimension_options.append('Audience')
        
        compare_dimension = st.selectbox("Group By", dimension_options, key="compare_dimension")
    
    col1, col2 = st.columns(2)
    with col1:
        chart_type_2 = st.selectbox("Chart Type", ["Grouped Bar", "Line", "Radar"], key="chart_type_2")
    with col2:
        normalize_data = st.checkbox("Normalize Data (0-100 scale)", value=False, key="normalize_kpi")
    
    if st.button("📊 Generate KPI Comparison", key="generate_kpi_comparison"):
        if selected_kpis and compare_dimension:
            try:
                # Map dimension to actual column
                dim_map = {
                    'Platform': 'Platform',
                    'Campaign': 'Campaign_Name',
                    'Placement': 'Placement',
                    'Audience': 'Audience' if 'Audience' in df.columns else 'Audience_Segment'
                }
                actual_dim = dim_map.get(compare_dimension, 'Platform')
                
                if actual_dim in df.columns:
                    # Aggregate data
                    agg_data = df.groupby(actual_dim)[selected_kpis].sum().reset_index()
                    
                    # Normalize if requested
                    if normalize_data:
                        for kpi in selected_kpis:
                            max_val = agg_data[kpi].max()
                            if max_val > 0:
                                agg_data[f"{kpi}_norm"] = (agg_data[kpi] / max_val) * 100
                        kpi_cols = [f"{kpi}_norm" for kpi in selected_kpis]
                    else:
                        kpi_cols = selected_kpis
                    
                    # Melt data for plotting
                    melted_data = agg_data.melt(
                        id_vars=[actual_dim],
                        value_vars=kpi_cols,
                        var_name='KPI',
                        value_name='Value'
                    )
                    
                    if chart_type_2 == "Grouped Bar":
                        fig = px.bar(
                            melted_data,
                            x='KPI',
                            y='Value',
                            color=actual_dim,
                            barmode='group',
                            title=f"KPI Comparison by {compare_dimension}"
                        )
                    elif chart_type_2 == "Line":
                        fig = px.line(
                            melted_data,
                            x='KPI',
                            y='Value',
                            color=actual_dim,
                            markers=True,
                            title=f"KPI Comparison by {compare_dimension}"
                        )
                    elif chart_type_2 == "Radar":
                        fig = go.Figure()
                        for dim_val in agg_data[actual_dim].unique():
                            dim_data = melted_data[melted_data[actual_dim] == dim_val]
                            fig.add_trace(go.Scatterpolar(
                                r=dim_data['Value'].tolist(),
                                theta=dim_data['KPI'].tolist(),
                                fill='toself',
                                name=str(dim_val)
                            ))
                        fig.update_layout(
                            polar=dict(radialaxis=dict(visible=True)),
                            title=f"KPI Radar: {compare_dimension}"
                        )
                    
                    fig.update_layout(template='plotly_dark')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"Column {actual_dim} not found in data")
            except Exception as e:
                st.error(f"Error creating KPI comparison: {str(e)[:200]}")
        else:
            st.warning("Please select at least one KPI and a dimension")
    
    st.divider()
    
    # ========================================
    # SECTION 3: SMART FILTERS (MOVED DOWN)
    # ========================================
    st.markdown("### 🎯 Smart Filters")
    
    # Initialize filter engine if needed
    if st.session_state.filter_engine is None and st.session_state.get('analytics_expert'):
        try:
            st.session_state.filter_engine = SmartFilterEngine()
        except:
            pass
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Platform filter
        platforms = ['All'] + sorted(df['Platform'].dropna().unique().tolist()) if 'Platform' in df.columns else ['All']
        selected_platform = st.selectbox("📱 Platform", platforms)
    
    with col2:
        # Date range filter
        if 'Date' in df.columns:
            try:
                min_date = pd.to_datetime(df['Date'], format='mixed', dayfirst=True).min()
                max_date = pd.to_datetime(df['Date'], format='mixed', dayfirst=True).max()
                date_range = st.date_input(
                    "📅 Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
            except Exception as e:
                st.warning(f"⚠️ Date parsing issue: {str(e)[:100]}")
                date_range = None
        else:
            date_range = None
    
    with col3:
        # Metric filter
        metric_options = ['Spend', 'Clicks', 'Conversions', 'Impressions', 'Revenue']
        available_metrics = [m for m in metric_options if m in df.columns]
        if available_metrics:
            selected_metric = st.selectbox("📊 Primary Metric", available_metrics)
        else:
            selected_metric = None
    
    # Secondary metric for dual-axis charts
    col1, col2, col3 = st.columns(3)
    with col1:
        secondary_options = [m for m in available_metrics if m != selected_metric] if available_metrics else []
        if secondary_options:
            secondary_metric = st.selectbox("📈 Secondary Metric", secondary_options, key="secondary_metric")
        else:
            secondary_metric = None
    
    with col2:
        # Analysis type selector
        analysis_types = [
            "Spend-Conversion Analysis",
            "Marketing Funnel",
            "Platform Comparison",
            "Weekly Trends",
            "Monthly Trends"
        ]
        selected_analysis = st.selectbox("🔍 Analysis Type", analysis_types)
    
    with col3:
        # Group by selector
        group_options = ['Platform']
        if 'Campaign_Name' in df.columns:
            group_options.append('Campaign')
        if 'Placement' in df.columns:
            group_options.append('Placement')
        if 'Ad_Type' in df.columns or 'AdType' in df.columns:
            group_options.append('Ad Type')
        if 'Creative' in df.columns:
            group_options.append('Creative')
        if 'Audience' in df.columns or 'Audience_Segment' in df.columns:
            group_options.append('Audience')
        if 'Geo' in df.columns or 'Geography' in df.columns or 'Country' in df.columns:
            group_options.append('Geo')
        if 'Device' in df.columns:
            group_options.append('Device')
        if 'Age' in df.columns or 'Age_Group' in df.columns:
            group_options.append('Age')
        
        group_by = st.selectbox("📊 Group By", group_options)
    
    # Advanced filters
    with st.expander("🔧 Advanced Filters"):
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Spend' in df.columns:
                min_spend = float(df['Spend'].min())
                max_spend = float(df['Spend'].max())
                spend_range = st.slider(
                    "Spend Range",
                    min_value=min_spend,
                    max_value=max_spend,
                    value=(min_spend, max_spend)
                )
            else:
                spend_range = None
        
        with col2:
            if 'Conversions' in df.columns:
                min_conv = float(df['Conversions'].min())
                max_conv = float(df['Conversions'].max())
                conv_range = st.slider(
                    "Conversions Range",
                    min_value=min_conv,
                    max_value=max_conv,
                    value=(min_conv, max_conv)
                )
            else:
                conv_range = None
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_platform != 'All' and 'Platform' in df.columns:
        filtered_df = filtered_df[filtered_df['Platform'] == selected_platform]
    
    if date_range and 'Date' in df.columns:
        if len(date_range) == 2:
            try:
                filtered_df['Date_parsed'] = pd.to_datetime(filtered_df['Date'], format='mixed', dayfirst=True)
                filtered_df = filtered_df[
                    (filtered_df['Date_parsed'] >= pd.to_datetime(date_range[0])) &
                    (filtered_df['Date_parsed'] <= pd.to_datetime(date_range[1]))
                ]
                filtered_df = filtered_df.drop('Date_parsed', axis=1)
            except Exception as e:
                st.warning(f"⚠️ Date filtering failed: {str(e)[:100]}")
    
    if spend_range and 'Spend' in df.columns:
        filtered_df = filtered_df[
            (filtered_df['Spend'] >= spend_range[0]) &
            (filtered_df['Spend'] <= spend_range[1])
        ]
    
    if conv_range and 'Conversions' in df.columns:
        filtered_df = filtered_df[
            (filtered_df['Conversions'] >= conv_range[0]) &
            (filtered_df['Conversions'] <= conv_range[1])
        ]
    
    st.divider()
    
    # ========================================
    # SECTION 4: FILTERED RESULTS & ANALYSIS
    # ========================================
    st.markdown(f"### 📊 Filtered Results ({len(filtered_df)} rows)")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'Spend' in filtered_df.columns:
            spend_val = filtered_df['Spend'].sum()
            st.metric("Total Spend", format_number(spend_val, 'currency'))
    
    with col2:
        if 'Conversions' in filtered_df.columns:
            conv_val = filtered_df['Conversions'].sum()
            st.metric("Total Conversions", format_number(conv_val, 'number'))
    
    with col3:
        if 'Clicks' in filtered_df.columns:
            clicks_val = filtered_df['Clicks'].sum()
            st.metric("Total Clicks", format_number(clicks_val, 'number'))
    
    with col4:
        if 'Impressions' in filtered_df.columns:
            imp_val = filtered_df['Impressions'].sum()
            st.metric("Total Impressions", format_number(imp_val, 'number'))
    
    st.divider()
    
    # Dual-Axis Visualizations
    if selected_metric and selected_metric in filtered_df.columns:
        if secondary_metric:
            chart_title = f"{selected_metric}-{secondary_metric} Analysis"
        else:
            chart_title = f"{selected_metric} Analysis"
        
        st.markdown(f"### 📈 {chart_title}")
        
        # Map group_by to actual column
        group_col_map = {
            'Platform': 'Platform',
            'Campaign': 'Campaign_Name',
            'Placement': 'Placement',
            'Ad Type': 'Ad_Type' if 'Ad_Type' in filtered_df.columns else 'AdType',
            'Creative': 'Creative',
            'Audience': 'Audience' if 'Audience' in filtered_df.columns else 'Audience_Segment',
            'Geo': 'Geo' if 'Geo' in filtered_df.columns else ('Geography' if 'Geography' in filtered_df.columns else 'Country'),
            'Device': 'Device',
            'Age': 'Age' if 'Age' in filtered_df.columns else 'Age_Group'
        }
        
        actual_group_col = group_col_map.get(group_by, 'Platform')
        
        # Create dual-axis chart
        if secondary_metric and secondary_metric in filtered_df.columns and actual_group_col in filtered_df.columns:
            try:
                fig = create_dual_axis_chart(
                    filtered_df,
                    x_col=actual_group_col,
                    primary_metric=selected_metric,
                    secondary_metric=secondary_metric,
                    title=f"{selected_metric} vs {secondary_metric} by {group_by}"
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create dual-axis chart: {e}")
                if actual_group_col in filtered_df.columns:
                    chart_data = filtered_df.groupby(actual_group_col)[selected_metric].sum().reset_index()
                    st.bar_chart(chart_data.set_index(actual_group_col))
        else:
            # Single metric chart
            if actual_group_col in filtered_df.columns:
                chart_data = filtered_df.groupby(actual_group_col)[selected_metric].sum().reset_index()
                fig = px.bar(
                    chart_data,
                    x=actual_group_col,
                    y=selected_metric,
                    title=f"{selected_metric} by {group_by}",
                    color=actual_group_col
                )
                fig.update_layout(template='plotly_dark')
                st.plotly_chart(fig, use_container_width=True)
        
        # ========================================
        # TIME SERIES - WEEKLY LINE CHART (IMPROVED)
        # ========================================
        if 'Date' in filtered_df.columns and secondary_metric:
            st.markdown("#### 📅 Weekly Time Series Analysis")
            try:
                # Parse dates
                filtered_df['Date_parsed'] = pd.to_datetime(filtered_df['Date'], format='mixed', dayfirst=True)
                
                # Aggregate by week
                weekly_data = filtered_df.set_index('Date_parsed').resample('W')[
                    [selected_metric, secondary_metric]
                ].sum().reset_index()
                
                # Create line chart with dual axis
                fig = go.Figure()
                
                # Primary metric (left axis)
                fig.add_trace(go.Scatter(
                    x=weekly_data['Date_parsed'],
                    y=weekly_data[selected_metric],
                    name=selected_metric,
                    mode='lines+markers',
                    line=dict(color='#667eea', width=3),
                    marker=dict(size=8)
                ))
                
                # Secondary metric (right axis)
                fig.add_trace(go.Scatter(
                    x=weekly_data['Date_parsed'],
                    y=weekly_data[secondary_metric],
                    name=secondary_metric,
                    mode='lines+markers',
                    line=dict(color='#f093fb', width=3),
                    marker=dict(size=8),
                    yaxis='y2'
                ))
                
                # Update layout with dual axes
                fig.update_layout(
                    title=f"Weekly Trend: {selected_metric} vs {secondary_metric}",
                    xaxis=dict(title='Week'),
                    yaxis=dict(title=selected_metric, side='left'),
                    yaxis2=dict(title=secondary_metric, side='right', overlaying='y'),
                    template='plotly_dark',
                    hovermode='x unified',
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create weekly time series: {e}")
        
        # Marketing Funnel
        if selected_analysis == "Marketing Funnel":
            st.markdown("#### 🔄 Marketing Funnel")
            funnel_metrics = ['Impressions', 'Clicks', 'Conversions']
            available_funnel = [m for m in funnel_metrics if m in filtered_df.columns]
            
            if len(available_funnel) >= 2:
                funnel_data = pd.DataFrame({
                    'Stage': available_funnel,
                    'Value': [filtered_df[m].sum() for m in available_funnel]
                })
                
                fig = go.Figure(go.Funnel(
                    y=funnel_data['Stage'],
                    x=funnel_data['Value'],
                    textinfo="value+percent initial",
                    marker=dict(color=['#667eea', '#764ba2', '#f093fb'])
                ))
                fig.update_layout(title="Marketing Funnel", template='plotly_dark')
                st.plotly_chart(fig, use_container_width=True)
    
    # ========================================
    # SECTION 5: SPEND-CLICK ANALYSIS BY MULTIPLE DIMENSIONS (NEW)
    # ========================================
    st.divider()
    st.markdown("### 💰 Spend-Click Analysis by Dimension")
    
    # Detect available dimensions
    dimension_map = {}
    
    # Platform (always available)
    if 'Platform' in filtered_df.columns:
        dimension_map['Platform'] = 'Platform'
    
    # Funnel Stage
    funnel_cols = ['Funnel_Stage', 'Stage', 'Funnel', 'Marketing_Funnel']
    for col in funnel_cols:
        if col in filtered_df.columns:
            dimension_map['Funnel Stage'] = col
            break
    
    # Source/Channel
    source_cols = ['Source', 'Channel', 'Traffic_Source', 'Medium', 'utm_source', 'utm_medium']
    for col in source_cols:
        if col in filtered_df.columns:
            dimension_map['Source/Channel'] = col
            break
    
    # Audience Type
    audience_cols = ['Audience', 'Audience_Type', 'Audience_Segment', 'Segment', 'Target_Audience']
    for col in audience_cols:
        if col in filtered_df.columns:
            dimension_map['Audience Type'] = col
            break
    
    # Demographics
    demo_cols = ['Age', 'Age_Group', 'Age_Range', 'Gender', 'Location', 'Geography', 'Geo', 'Country', 'Region']
    for col in demo_cols:
        if col in filtered_df.columns:
            dimension_map['Demographics'] = col
            break
    
    # Campaign Type
    campaign_type_cols = ['Campaign_Type', 'CampaignType', 'Type', 'Objective', 'Campaign_Objective']
    for col in campaign_type_cols:
        if col in filtered_df.columns:
            dimension_map['Campaign Type'] = col
            break
    
    if dimension_map:
        selected_dimension = st.selectbox(
            "Select Dimension for Analysis",
            list(dimension_map.keys()),
            key="spend_click_dimension"
        )
        
        if selected_dimension and 'Spend' in filtered_df.columns and 'Clicks' in filtered_df.columns:
            actual_col = dimension_map[selected_dimension]
            
            try:
                # Aggregate by dimension
                analysis_data = filtered_df.groupby(actual_col).agg({
                    'Spend': 'sum',
                    'Clicks': 'sum'
                }).reset_index()
                
                # Create scatter plot
                fig = px.scatter(
                    analysis_data,
                    x='Spend',
                    y='Clicks',
                    text=actual_col,
                    title=f"Spend vs Clicks by {selected_dimension}",
                    size='Clicks',
                    color=actual_col,
                    hover_data={actual_col: True, 'Spend': ':,.0f', 'Clicks': ':,.0f'}
                )
                
                fig.update_traces(textposition='top center', textfont_size=10)
                fig.update_layout(
                    template='plotly_dark',
                    xaxis_title="Total Spend ($)",
                    yaxis_title="Total Clicks",
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show data table
                st.markdown(f"**{selected_dimension} Performance:**")
                analysis_data['CPC'] = analysis_data['Spend'] / analysis_data['Clicks']
                analysis_data = analysis_data.sort_values('Spend', ascending=False)
                st.dataframe(
                    analysis_data.style.format({
                        'Spend': '${:,.2f}',
                        'Clicks': '{:,.0f}',
                        'CPC': '${:.2f}'
                    }),
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error creating spend-click analysis: {str(e)[:200]}")
    else:
        st.info("No additional dimensions found for spend-click analysis. Available: Platform only.")
    
    # Data table
    st.divider()
    with st.expander("📋 View Filtered Data"):
        st.dataframe(filtered_df, use_container_width=True, height=400)
    
    # Export options
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Export to CSV", key="deep_dive_export"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="filtered_data.csv",
                mime="text/csv"
            )
