import reflex as rx
from ..state import State
from ..components.layout import require_auth

def diagnostics_content():
    return rx.vstack(
        rx.heading("🔬 Smart Performance Diagnostics", size="8"),
        
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Causal Analysis", value="causal"),
                rx.tabs.trigger("Driver Analysis", value="driver"),
            ),
            
            rx.tabs.content(
                rx.vstack(
                    rx.heading("Target Metric Breakdown", size="4"),
                    rx.hstack(
                        rx.select(
                            ["ROAS", "CPA", "CTR", "CVR", "CPC"],
                            label="Metric",
                            value=State.causal_metric,
                            on_change=State.set_causal_metric
                        ),
                        rx.slider(
                             min=7, max=90, default_value=[30],
                             label="Lookback Days",
                             on_change=State.set_lookback_days
                        ),
                        rx.button("Run Causal Analysis", on_click=State.run_causal_analysis, loading=State.is_running_causal),
                        align_items="end",
                        spacing="4"
                    ),
                    rx.cond(
                        State.causal_waterfall,
                        rx.vstack(
                            rx.plotly(data=State.causal_waterfall, height="500px"),
                            rx.grid(
                                rx.vstack(
                                    rx.text("Data Insights", weight="bold"),
                                    rx.foreach(
                                        State.causal_insights,
                                        lambda x: rx.callout(x)
                                    ),
                                    width="100%"
                                ),
                                rx.vstack(
                                    rx.text("Knowledge Base Recommendations (RAG)", weight="bold", color_scheme="violet"),
                                    rx.foreach(
                                        State.causal_recommendations,
                                        lambda x: rx.callout(x, color_scheme="violet")
                                    ),
                                    width="100%"
                                ),
                                columns="2",
                                spacing="4",
                                width="100%"
                            )
                        )
                    ),
                    spacing="5",
                    padding="4"
                ),
                value="causal",
            ),
            
            rx.tabs.content(
                rx.vstack(
                    rx.heading("Driver Analysis", size="4"),
                    rx.hstack(
                        rx.select(
                            ["ROAS", "CPA", "CTR", "CVR", "CPC"], # Should be dynamic based on cols
                            label="Target Metric",
                            value=State.driver_target,
                            on_change=State.set_driver_target # Need setter
                        ),
                        rx.button("Run Driver Analysis", on_click=State.run_driver_analysis, loading=State.is_running_driver),
                        align_items="end",
                        spacing="4"
                    ),
                    rx.cond(
                        State.driver_chart,
                        rx.vstack(
                             rx.text(f"Model Quality: {State.driver_result['model_score']}"),
                             rx.plotly(data=State.driver_chart, height="500px"),
                             width="100%"
                        )
                    ),
                    spacing="5",
                    padding="4"
                ),
                value="driver",
            ),
            
            default_value="causal",
            width="100%",
        ),
        
        spacing="6",
        width="100%",
    )

def diagnostics_page():
    return require_auth(diagnostics_content())
