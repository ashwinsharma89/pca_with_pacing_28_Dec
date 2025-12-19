import reflex as rx
from ..state import State
from ..style import sidebar_style

def sidebar_item(text: str, icon: str, url: str) -> rx.Component:
    """Sidebar navigation item."""
    return rx.link(
        rx.hstack(
            rx.icon(icon, size=20),
            rx.text(text, size="3", weight="medium"),
            spacing="3",
            width="100%",
            padding="12px",
            border_radius="12px",
            transition="background 0.2s",
            _hover={
                "background": "rgba(255, 255, 255, 0.1)",
                "color": "white",
            },
            color="rgba(255, 255, 255, 0.7)",
        ),
        href=url,
        width="100%",
        underline="none",
    )

def sidebar() -> rx.Component:
    return rx.vstack(
        # Logo / Brand
        rx.hstack(
            rx.box(
                rx.icon("aperture", size=24, color="violet"),
                padding="8px",
                background="rgba(139, 92, 246, 0.2)",
                border_radius="8px",
            ),
            rx.text("MediaAgent", size="5", weight="bold", color="white"),
            spacing="3",
            align_items="center",
            padding="24px 16px",
            width="100%",
        ),
        
        rx.divider(background="rgba(255, 255, 255, 0.1)"),
        
        # Navigation
        rx.vstack(
            sidebar_item("Dashboard", "layout-dashboard", "/"),
            sidebar_item("Upload Data", "upload", "/upload"), # Added
            sidebar_item("AI Analysis", "brain-circuit", "/analysis"),
            sidebar_item("Q&A Assistant", "message-square", "/qa"), # Added
            sidebar_item("Visualizations", "bar-chart-2", "/visualizations"),
            sidebar_item("Deep Dive", "layers", "/deep-dive"), 
            sidebar_item("Predictive", "trending-up", "/predictive"),
            sidebar_item("Reporting", "file-text", "/reporting"),
            sidebar_item("Diagnostics", "stethoscope", "/diagnostics"),
            spacing="1",
            width="100%",
            padding="16px",
        ),
        
        rx.spacer(),
        
        # Bottom Actions
        rx.vstack(
             rx.cond(
                State.user_authenticated,
                rx.hstack(
                    rx.avatar(fallback=State.username[0], size="3"),
                    rx.vstack(
                        rx.text(State.username, size="2", weight="bold"),
                        rx.text("Pro Member", size="1", color="gray"),
                        spacing="0"
                    ),
                    spacing="3",
                    padding="12px",
                    width="100%",
                    background="rgba(255,255,255,0.05)",
                    border_radius="12px",
                )
            ),
            rx.button(
                rx.hstack(rx.icon("log-out"), rx.text("Logout")),
                on_click=State.logout,
                variant="ghost",
                color_scheme="red",
                width="100%",
                justify_content="start",
            ),
            width="100%",
            padding="16px",
            spacing="4",
        ),
        
        style=sidebar_style,
    )

def sidebar_layout(child: rx.Component) -> rx.Component:
    """Wrapper for pages with sidebar navigation."""
    return rx.hstack(
        sidebar(),
        rx.box(
            child,
            width="100%",
            height="100vh",
            overflow_y="auto",
            padding="0px",
            # background="radial-gradient(circle at 50% 10%, rgba(120, 119, 198, 0.1) 0%, rgba(0, 0, 0, 0) 40%)",
        ),
        spacing="0",
        width="100%",
        height="100vh",
        background="#050510",
    )
