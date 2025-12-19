import reflex as rx
from ..state.viz import VizState as State
from ..components.layout import require_auth

def stat_card(label: str, value: str, subtext: str = None):
    """Reusable statistic card."""
    return rx.card(
        rx.vstack(
            rx.text(label, size="2", color_scheme="gray"),
            rx.text(value, size="6", weight="bold"),
            rx.cond(
                subtext,
                rx.text(subtext, size="1", color_scheme="green"),
                rx.box()
            ),
            spacing="1",
        ),
        size="2",
        width="100%"
    )

def smart_filters_panel():
    """Enhanced Smart Insights Filters Panel."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("filter", color="violet"),
                rx.heading("Smart Insights Filters", size="4"),
                rx.spacer(),
                rx.text("Refine your analysis by multiple dimensions", size="2", color="gray"),
                width="100%",
                align="center",
            ),
            
            rx.divider(),
            
            # Row 1: Core Filters
            rx.grid(
                # Platform
                rx.vstack(
                    rx.text("Platform", size="2", weight="bold"),
                    rx.select(
                        State.platform_options,
                        placeholder="Select Platform",
                        value=State.selected_platforms[0],
                        on_change=lambda val: State.set_selected_platforms([val]),
                        size="3",
                        width="100%",
                    ),
                    spacing="2"
                ),
                
                # Date Range
                rx.vstack(
                    rx.text("Date Range", size="2", weight="bold"),
                    rx.hstack(
                        rx.input(
                            type="date",
                            value=State.filter_date_range[0],
                            on_change=State.set_start_date,
                            width="140px",
                            size="2"
                        ),
                        rx.text("to", size="2", color="gray"),
                        rx.input(
                            type="date",
                            value=State.filter_date_range[1],
                            on_change=State.set_end_date,
                            width="140px",
                            size="2"
                        ),
                        spacing="2",
                        align_items="center"
                    ),
                    spacing="2"
                ),
                
                # Analysis Type
                rx.vstack(
                    rx.text("Analysis Type", size="2", weight="bold"),
                    rx.select(
                        ["Spend-Conversion Analysis", "Trend Analysis", "Cohort Analysis", "Attribution Model", "Creative Performance", "Funnel Drop-off"],
                        placeholder="Select Type",
                        default_value="Spend-Conversion Analysis",
                        size="3",
                        width="100%",
                    ),
                    spacing="2"
                ),
                
                # Primary Grouping
                rx.vstack(
                    rx.text("Primary Grouping", size="2", weight="bold"),
                    rx.select(
                        ["Platform", "Campaign", "Ad Group", "Creative", "Weekly", "Monthly"],
                        default_value="Platform",
                        size="3",
                        width="100%",
                    ),
                    spacing="2"
                ),
                
                columns="4",
                spacing="5",
                width="100%",
            ),
            
            rx.text("Additional Dimensions", size="2", weight="bold", padding_top="2"),
            
            rx.grid(
                rx.vstack(
                     rx.text("Audience", size="1", color="gray"),
                     rx.select(
                         State.audience_options,
                         placeholder="All Audiences", 
                         on_change=lambda val: State.set_selected_audiences([val]),
                         size="2"
                    )
                ),
                rx.vstack(
                     rx.text("Placement", size="1", color="gray"),
                     rx.select(
                         State.placement_options,
                         placeholder="All Placements",
                         on_change=lambda val: State.set_selected_placements([val]), 
                         size="2"
                    )
                ),
                 rx.vstack(
                      rx.text("Ad Type", size="1", color="gray"),
                      rx.select(
                          State.ad_type_options,
                          placeholder="All Ad Types",
                          on_change=lambda val: State.set_selected_ad_types([val]),
                          size="2"
                     )
                ),
                 rx.vstack(
                     rx.text("Funnel Stage", size="1", color="gray"),
                     rx.select(
                         State.funnel_options,
                         placeholder="All Stages",
                         on_change=lambda val: State.set_selected_funnel_stages([val]),
                         size="2"
                    )
                ),
                columns="4",
                spacing="4",
                width="100%"
            ),

            spacing="5",
            width="100%",
            padding="4",
        ),
        size="4",
        variant="surface",
        width="100%",
    )


def performance_overview():
    """Performance Metrics Overview."""
    return rx.hstack(
        rx.image(src="/assets/chart_icon_placeholder.png", width="32px", height="32px"), # Placeholder icon
        rx.heading(rx.text(f"Filtered Results ({State.total_rows} rows)", size="4")),
        rx.spacer(),
        rx.hstack(
            # Using simple text stacks instead of cards for a cleaner "Overview" look like Streamlit
            rx.vstack(
                rx.text("Total Spend", size="1", weight="bold"),
                rx.heading(State.total_spend, size="6"),
            ),
            rx.vstack(
                rx.text("Total Conversions", size="1", weight="bold"),
                rx.heading(State.total_conversions, size="6"),
            ),
            rx.vstack(
                rx.text("Total Clicks", size="1", weight="bold"),
                rx.heading(State.total_clicks, size="6"),
            ),
            rx.vstack(
                rx.text("Total Impressions", size="1", weight="bold"),
                rx.heading(State.total_impressions, size="6"),
            ),
            spacing="8",
            align_items="start"
        ),
        width="100%",
        padding_y="4",
        align_items="center"
    )

def custom_chart_builder():
    """First Custom Chart Builder Component."""
    return rx.vstack(
        rx.hstack(
            rx.icon("palette", color="orange"),
            rx.heading("Custom Chart Builder", size="4"),
            align_items="center",
            spacing="2"
        ),
        rx.text("Build custom visualizations with your data", size="2", color_scheme="gray"),
        
        # Controls
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.select(
                        ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart", "Box Plot", "Area Chart", "Heatmap"],
                        placeholder="Chart Type",
                        label="Chart Type",
                        value=State.chart_type,
                        on_change=State.set_chart_type,
                        width="200px"
                    ),
                    rx.select(
                        State.columns,
                        placeholder="Select X-Axis",
                        label="X-Axis",
                        value=State.x_axis,
                        on_change=State.update_x_axis,
                        width="300px"
                    ),
                    rx.select(
                        State.numeric_columns,
                        placeholder="Select Y-Axis",
                        label="Y-Axis (Metric)",
                        value=State.y_axis,
                        on_change=State.update_y_axis,
                        width="300px"
                    ),
                    width="100%",
                    spacing="4"
                ),
                rx.hstack(
                    rx.select(
                        State.color_options,
                        placeholder="Color By",
                        label="Color By (Optional)",
                        value=State.color_by,
                        on_change=State.set_color_by,
                         width="300px"
                    ),
                    rx.select(
                        ["Sum", "Mean", "Count", "Max", "Min"],
                        placeholder="Aggregation",
                        label="Aggregation",
                        value=State.aggregation,
                        on_change=State.set_aggregation,
                        width="300px"
                    ),
                    width="100%",
                    spacing="4"
                ),
                rx.button(
                    "Generate Custom Chart",
                    on_click=State.generate_custom_chart,
                    width="200px",
                    color_scheme="indigo"
                ),
                spacing="4",
                width="100%"
            ),
            width="100%"
        ),
        
        # Chart Display
        rx.cond(
            State.custom_chart_figure,
            rx.plotly(data=State.custom_chart_figure, height="500px", width="100%"),
            rx.center(rx.text("Select options and click Generate", color_scheme="gray"), padding="10")
        ),
        width="100%",
        spacing="4"
    )

def custom_chart_builder_2():
    """Second Custom Chart Builder Component."""
    return rx.vstack(
        rx.hstack(
            rx.icon("palette", color="orange"),
            rx.heading("Custom Chart Builder-2", size="4"),
            align_items="center",
            spacing="2"
        ),
        rx.text("Compare multiple KPIs side-by-side or create a secondary view", size="2", color_scheme="gray"),
        
        # Controls (Bound to _2 variables)
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.select(
                        ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart", "Box Plot", "Area Chart", "Heatmap"],
                        placeholder="Chart Type",
                        label="Chart Type",
                        value=State.chart_type_2,
                        on_change=State.set_chart_type_2,
                        width="200px"
                    ),
                    rx.select(
                        State.columns,
                        placeholder="Select X-Axis",
                        label="X-Axis",
                        value=State.x_axis_2,
                        on_change=State.update_x_axis_2,
                        width="300px"
                    ),
                    rx.select(
                        State.numeric_columns,
                        placeholder="Select Y-Axis",
                        label="Y-Axis (Metric)",
                        value=State.y_axis_2,
                        on_change=State.update_y_axis_2,
                        width="300px"
                    ),
                    width="100%",
                    spacing="4"
                ),
                rx.hstack(
                    rx.select(
                        State.color_options,
                        placeholder="Color By",
                        label="Color By (Optional)",
                        value=State.color_by_2,
                        on_change=State.set_color_by_2,
                         width="300px"
                    ),
                    rx.select(
                        ["Sum", "Mean", "Count", "Max", "Min"],
                        placeholder="Aggregation",
                        label="Aggregation",
                        value=State.aggregation_2,
                        on_change=State.set_aggregation_2,
                        width="300px"
                    ),
                    width="100%",
                    spacing="4"
                ),
                rx.button(
                    "Generate Custom Chart 2",
                    on_click=State.generate_custom_chart_2,
                    width="200px",
                    color_scheme="indigo"
                ),
                spacing="4",
                width="100%"
            ),
            width="100%"
        ),
        
        # Chart Display
        rx.cond(
            State.custom_chart_figure_2,
            rx.plotly(data=State.custom_chart_figure_2, height="500px", width="100%"),
            rx.center(rx.text("Select options and click Generate", color_scheme="gray"), padding="10")
        ),
        width="100%",
        spacing="4"
    )

def kpi_comparison_builder():
    """KPI Comparison Tab Content."""
    return rx.vstack(
        rx.heading("KPI Comparison", size="5"),
        rx.text("Compare up to 3 metrics across a dimension.", color_scheme="gray"),
        
        rx.card(
            rx.vstack(
                rx.text("Select KPIs to Compare (Max 3):", weight="bold"),
                rx.box(
                    rx.hstack(
                        rx.foreach(
                            State.numeric_columns,
                            lambda kpi: rx.checkbox(
                                kpi,
                                on_change=lambda checked: State.toggle_kpi(kpi, checked),
                                checked=State.selected_kpis.contains(kpi)
                            )
                        ),
                        spacing="4",
                        wrap="wrap"
                    ),
                    border="1px solid #333",
                    padding="2",
                    border_radius="md",
                    width="100%"
                ),
                rx.hstack(
                    rx.select(
                        State.columns,
                        placeholder="Group By (Dimension)",
                        label="Group By",
                        value=State.compare_dimension,
                        on_change=State.set_compare_dimension,
                    ),
                    rx.select(
                        ["Grouped Bar", "Line", "Radar", "Dual Axis"],
                        placeholder="Chart Type",
                        label="Chart Type",
                        value=State.comparison_chart_type,
                        on_change=State.set_comparison_chart_type,
                    ),
                    rx.checkbox(
                        "Normalize Data (0-100 scale)",
                        checked=State.normalize,
                        on_change=State.set_normalize
                    ),
                    align_items="end",
                    spacing="4"
                ),
                rx.button(
                    "Generate KPI Comparison",
                    on_click=State.generate_comparison_chart,
                    color_scheme="violet"
                ),
                spacing="4",
                width="100%"
            )
        ),
        rx.cond(
            State.comparison_chart_figure,
            rx.plotly(data=State.comparison_chart_figure, height="600px", width="100%"),
            rx.text("Select KPIs and dimension to compare.")
        ),
        width="100%",
        spacing="4"
    )

def visualizations_content():
    return rx.vstack(
        rx.heading("In-Depth Analysis", size="8"),
        
        # 1. Smart Filters
        smart_filters_panel(),
        
        # 2. Performance Overview
        performance_overview(),
        
        rx.divider(),
        
        # 3. Main Content (Chart Builders & Tabs)
        custom_chart_builder(),
        
        rx.divider(),
        
        custom_chart_builder_2(),
        
        rx.divider(),
        
        # Keeping existing features in tabs below
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Custom Builder", value="custom"), # Keeping this for parity, but content is essentially duplicated above. Maybe rename?
                rx.tabs.trigger("KPI Comparison", value="comparison"),
                rx.tabs.trigger("Conversion Funnel", value="funnel"),
                rx.tabs.trigger("Correlation Matrix", value="correlation"),
            ),
            rx.tabs.content(
                rx.text("Use the Chart Builders above for custom analysis.", padding="4", color_scheme="gray"),
                value="custom"
            ),
            rx.tabs.content(
                kpi_comparison_builder(),
                value="comparison"
            ),
            rx.tabs.content(
                rx.vstack(
                    rx.button("Generate Funnel", on_click=State.generate_funnel_chart),
                     rx.cond(
                        State.funnel_figure,
                        rx.plotly(data=State.funnel_figure, height="600px", width="100%"),
                        rx.text("Click to generate funnel.")
                    ),
                    width="100%"
                ),
                value="funnel"
            ),
            rx.tabs.content(
                 rx.vstack(
                    rx.button("Generate Correlation Matrix", on_click=State.generate_correlation_matrix),
                     rx.cond(
                        State.correlation_figure,
                        rx.plotly(data=State.correlation_figure, height="600px", width="100%"),
                        rx.text("Click to generate matrix.")
                    ),
                    width="100%"
                ),
                value="correlation"
            ),
            width="100%"
        ),
        
        width="100%",
        spacing="6",
    )

def visualizations_page():
    return require_auth(
        rx.box(
            rx.vstack(
                visualizations_content(),
                width="100%",
                padding="1.5em", 
                spacing="6",
            ),
            width="100%",
            on_mount=State.update_filter_options
        )
    )
