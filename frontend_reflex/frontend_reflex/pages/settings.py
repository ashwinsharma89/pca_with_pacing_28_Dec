import reflex as rx
from ..components.layout import require_auth

def settings_content():
    return rx.vstack(
        rx.heading("⚙️ Settings", size="8"),
        rx.text("Configure application settings."),
        rx.card(
            rx.vstack(
                rx.text("User Profile", weight="bold"),
                rx.text("Settings coming soon..."),
            ),
            width="100%",
        ),
        spacing="6",
        width="100%",
    )

def settings_page():
    return require_auth(settings_content())
