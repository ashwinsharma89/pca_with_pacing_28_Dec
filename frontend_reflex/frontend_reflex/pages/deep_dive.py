import reflex as rx
from ..state import State
from ..components.layout import require_auth

def deep_dive_content():
    return rx.vstack(
        rx.heading("🔍 In-Depth Analysis", size="8"),
        
        rx.callout.root(
            rx.callout.icon(rx.icon("info")),
            rx.callout.text("KPI Comparison: Select multiple metrics to compare across dimensions."),
            color_scheme="blue",
        ),
        
        rx.card(
            rx.vstack(
                rx.heading("Multi-Metric Comparison", size="5"),
                
                # Controls
                rx.flex(
                    rx.vstack(
                        rx.text("Select Metrics (Max 3):", weight="bold"),
                        rx.hstack(
                            rx.checkbox("Spend", 
                                checked=State.selected_kpis.contains("Spend"),
                                on_change=lambda x: State.toggle_kpi("Spend", x)),
                            rx.checkbox("Clicks", 
                                checked=State.selected_kpis.contains("Clicks"),
                                on_change=lambda x: State.toggle_kpi("Clicks", x)),
                            rx.checkbox("Conversions", 
                                checked=State.selected_kpis.contains("Conversions"),
                                on_change=lambda x: State.toggle_kpi("Conversions", x)),
                            rx.checkbox("Impressions", 
                                checked=State.selected_kpis.contains("Impressions"),
                                on_change=lambda x: State.toggle_kpi("Impressions", x)),
                            rx.checkbox("ROAS", 
                                checked=State.selected_kpis.contains("ROAS"),
                                on_change=lambda x: State.toggle_kpi("ROAS", x)),
                            spacing="4",
                            wrap="wrap",
                        ),
                        spacing="2",
                    ),
                    
                    rx.vstack(
                         rx.text("Dimension:", weight="bold"),
                         rx.select(
                             ["Platform", "Campaign", "Date"], 
                             value=State.compare_dimension,
                             on_change=State.set_compare_dimension
                         ),
                    ),
                    
                    rx.button("Compare Metrics", on_click=State.generate_comparison_chart, size="3"),
                    
                    gap="6",
                    align="end",
                    width="100%",
                ),
                
                rx.divider(),
                
                rx.cond(
                    State.comparison_chart_figure,
                    rx.card(
                         rx.plotly(data=State.comparison_chart_figure, height="600px"),
                         width="100%",
                         variant="ghost",
                    ),
                    rx.text("Select metrics and click Compare.", color="gray"),
                ),
                
                width="100%",
                spacing="5",
                padding="4",
            ),
            width="100%",
            variant="surface",
        ),
        
        spacing="6",
        width="100%",
    )

def deep_dive_page():
    return require_auth(deep_dive_content())
