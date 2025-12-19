import reflex as rx
from ..state.analysis import AnalysisState
from ..components.sidebar import sidebar_layout
from ..style import metric_card_style

def analysis_content() -> rx.Component:
    return rx.vstack(
        rx.heading("🧠 AI Analysis", size="8", margin_bottom="4"),
        
        # Controls
        rx.card(
            rx.vstack(
                rx.text("Analysis Configuration", weight="bold", size="4", margin_bottom="2"),
                rx.hstack(
                    rx.vstack(
                        rx.checkbox("Use RAG Knowledge Base", checked=AnalysisState.use_rag, on_change=AnalysisState.set_use_rag),
                        rx.text("Enhance analysis with verified marketing knowledge.", size="1", color="gray"),
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.checkbox("Include Industry Benchmarks", checked=AnalysisState.include_benchmarks, on_change=AnalysisState.set_include_benchmarks),
                        rx.text("Compare performance against industry standards.", size="1", color="gray"),
                         spacing="1",
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.hstack(
                             rx.cond(AnalysisState.is_analyzing, rx.spinner(), rx.icon("sparkles")),
                             rx.text("Run AI Analysis"),
                             spacing="2"
                        ),
                        on_click=AnalysisState.run_analysis,
                        disabled=AnalysisState.is_analyzing,
                        size="3",
                        variant="surface",
                        color_scheme="violet",
                    ),
                    width="100%",
                    align_items="center",
                    spacing="6",
                ),
                padding="6",
            ),
            width="100%",
            variant="ghost",
            background="rgba(255, 255, 255, 0.03)",
            border="1px solid rgba(255, 255, 255, 0.05)",
        ),
        
        rx.cond(
            AnalysisState.analysis_complete,
            rx.vstack(
                # Executive Summary
                rx.card(
                    rx.vstack(
                        rx.hstack(rx.icon("file-text", color="violet"), rx.heading("Executive Summary", size="6")),
                        rx.divider(),
                        rx.markdown(AnalysisState.executive_summary),
                        rx.accordion.root(
                            rx.accordion.item(
                                header="View Detailed Analysis",
                                content=rx.markdown(AnalysisState.detailed_summary),
                            ),
                            width="100%",
                            variant="soft",
                        ),
                        spacing="4",
                        padding="6",
                    ),
                    width="100%",
                    style=metric_card_style,
                ),
                
                # Insights Grid
                rx.heading("💡 Key Insights", size="6", margin_top="4"),
                rx.grid(
                    rx.foreach(
                        AnalysisState.insights,
                        lambda insight: rx.card(
                            rx.hstack(
                                rx.icon("lightbulb", color="yellow"),
                                rx.text(insight, size="2"),
                                align_items="start",
                                spacing="3"
                            ),
                            style=metric_card_style,
                            height="100%",
                        )
                    ),
                    columns="2",
                    spacing="4",
                    width="100%",
                ),
                
                # Recommendations Grid
                rx.heading("🎯 Strategic Recommendations", size="6", margin_top="4"),
                rx.vstack(
                    rx.foreach(
                        AnalysisState.recommendations,
                        lambda rec: rx.card(
                             rx.hstack(
                                rx.icon("target", color="red"),
                                rx.text(rec, size="2"),
                                align_items="center",
                                spacing="3"
                            ),
                            style={**metric_card_style, "border_left": "4px solid var(--violet-9)"},
                            width="100%",
                        )
                    ),
                    spacing="3",
                    width="100%",
                ),
                
                spacing="5",
                width="100%",
            ),
            # Empty State
            rx.center(
                rx.vstack(
                    rx.icon("bot", size=64, color="gray"),
                    rx.text("Ready to analyze your campaign data.", size="4", color="gray"),
                    rx.text("configure options above and click Run.", size="2", color="gray"),
                    spacing="2",
                    align_items="center",
                ),
                padding_y="64px",
                width="100%",
            )
        ),
        
        spacing="6",
        width="100%",
        padding="8",
    )

def analysis() -> rx.Component:
    return sidebar_layout(
        analysis_content()
    )
