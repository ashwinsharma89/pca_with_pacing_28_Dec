import reflex as rx
from ..state import State
from .sidebar import sidebar
from .filter_bar import filter_bar

def layout(content: rx.Component) -> rx.Component:
    return rx.hstack(
        # Sidebar
        rx.box(
            sidebar(),
            display=["none", "none", "block"], 
            width="250px", 
            min_height="100vh",
            height="100%",
            position="sticky",
            top="0",
            z_index="10",
        ),
        
        # Main Content Area
        rx.vstack(
            # Top Bar (Title/Search placeholder + User Profile placeholder)
            # For now simplified: Just filter bar below.
            
            # Filter Bar (Sticky)
            rx.box(
                filter_bar(),
                position="sticky",
                top="0",
                z_index="9",
                width="100%",
                padding="4",
                backdrop_filter="blur(10px)",
                background="rgba(5, 5, 16, 0.8)", # Match bg with opacity
            ),
            
            # Page Content
            rx.box(
                content,
                width="100%",
                padding="4",
                padding_bottom="100px", # Space for footer
            ),
            width="100%",
            min_height="100vh",
            align_items="start",
        ),
        width="100%",
        spacing="0",
    )

def require_auth(page_content: rx.Component) -> rx.Component:
    return rx.cond(
        State.user_authenticated,
        layout(page_content),
        login_form(),
    )

def login_form() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("Media Analytics Agent", size="8", margin_bottom="4"),
            rx.card(
                rx.vstack(
                    rx.heading("Login", size="8"),
                    rx.text("Enter your credentials to continue.", size="3", color="gray"),
                    
                    # Controlled Inputs
                    rx.vstack(
                        rx.input(
                            placeholder="Username", 
                            value=State.username,
                            on_change=State.set_username,
                            width="100%",
                        ),
                        rx.input(
                            placeholder="Password", 
                            type="password", 
                            value=State.password,
                            on_change=State.set_password,
                            width="100%",
                        ),
                        rx.button(
                            "Sign In", 
                            on_click=State.login, 
                            width="100%", 
                            size="3",
                            loading=State.is_logging_in,
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    spacing="6",
                    align_items="center",
                    padding="6",
                    width="400px",
                ),
                variant="surface",
                size="4",
            ),
            height="100vh",
            justify="center",
            spacing="4",
        ),
        width="100%",
        height="100vh",
        background="radial-gradient(circle at 50% 50%, rgba(120, 40, 200, 0.1) 0%, rgba(5, 5, 16, 1) 100%)",
    )
