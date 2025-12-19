import reflex as rx
from ..state.chat import ChatState
from ..components.sidebar import sidebar_layout

def message_bubble(message: dict) -> rx.Component:
    """A single message bubble."""
    return rx.box(
        rx.text(
            message["content"],
            color=rx.cond(message["role"] == "user", "white", "gray.200"),
        ),
        padding="12px 16px",
        border_radius="16px",
        background=rx.cond(
            message["role"] == "user",
            rx.color("violet", 9),
            "rgba(255, 255, 255, 0.1)",
        ),
        align_self=rx.cond(
            message["role"] == "user",
            "flex-end",
            "flex-start",
        ),
        margin_bottom="8px",
        max_width="80%",
    )

def qa_content() -> rx.Component:
    return rx.vstack(
        rx.heading("💬 AI Assistant", size="8", margin_bottom="4"),
        
        # Chat Window
        rx.card(
            rx.vstack(
                # Messages Area
                rx.scroll_area(
                    rx.vstack(
                        rx.foreach(
                            ChatState.messages,
                            message_bubble
                        ),
                        rx.cond(
                            ChatState.is_processing,
                            rx.hstack(
                                rx.spinner(size="1", color="violet"),
                                rx.text("Thinking...", size="1", color="gray"),
                                spacing="2",
                                padding="12px"
                            )
                        ),
                        width="100%",
                        align_items="stretch",
                    ),
                    height="60vh",
                    type="always",
                    scrollbars="vertical",
                    padding="4",
                ),
                
                rx.divider(opacity=0.1),
                
                # Input Area
                rx.hstack(
                    rx.input(
                        placeholder="Ask a question about your campaign data...",
                        value=ChatState.input_value,
                        on_change=ChatState.set_input_value,
                        width="100%",
                        on_key_down=lambda key: rx.cond(
                            key == "Enter",
                            ChatState.process_message,
                            None
                        )
                    ),
                    rx.button(
                        rx.icon("send", size=18),
                        on_click=ChatState.process_message,
                        disabled=ChatState.is_processing,
                        size="3",
                        variant="surface",
                        color_scheme="violet",
                    ),
                    width="100%",
                    padding="4",
                    spacing="3",
                    align_items="center"
                ),
                spacing="0",
            ),
            width="100%",
            padding="0",
            variant="ghost",
            border="1px solid rgba(255, 255, 255, 0.1)",
            background="rgba(255, 255, 255, 0.03)",
        ),
        
        # Helper text
        rx.hstack(
            rx.icon("info", size=16, color="gray"),
            rx.text("Pro tip: You can ask for aggregations like 'Total spend by platform' or specific insights.", size="1", color="gray"),
            spacing="2",
            align_items="center",
            opacity=0.6,
        ),
        
        width="100%",
        spacing="4",
        padding="8",
    )

def qa_page() -> rx.Component:
    return sidebar_layout(
        qa_content()
    )
