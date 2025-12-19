import reflex as rx
from ..state import State
from ..components.layout import require_auth

def dashboard_content():
    return rx.vstack(
        rx.heading("🏠 Welcome to PCA Agent", size="8"),
        rx.text(
            "Performance Campaign Analytics Agent - Modular, Production-Ready, AI-Powered.",
            size="4",
            color="gray",
        ),
        
        rx.divider(),
        
        # Quick Stats Row
        rx.heading("📈 Quick Stats", size="5"),
        rx.grid(
            rx.card(
                rx.vstack(
                    rx.text("Total Rows", size="1", weight="bold"),
                    rx.heading(State.total_rows, size="6"),
                )
            ),
            rx.card(
                rx.vstack(
                    rx.text("Total Spend", size="1", weight="bold"),
                    rx.heading(State.total_spend, size="6", color_scheme="blue"),
                )
            ),
            rx.card(
                rx.vstack(
                    rx.text("Total Clicks", size="1", weight="bold"),
                    rx.heading(State.total_clicks, size="6", color_scheme="green"),
                )
            ),
            rx.card(
                rx.vstack(
                    rx.text("Total Conversions", size="1", weight="bold"),
                    rx.heading(State.total_conversions, size="6", color_scheme="purple"),
                )
            ),
            columns="4",
            spacing="4",
            width="100%",
        ),
        
        rx.divider(),
        
        rx.heading("📁 Data Upload", size="5"),
        rx.card(
            rx.vstack(
                rx.text("Upload your campaign data CSV/Excel"),
                
                # Excel Multi-Sheet Selector
                rx.cond(
                    State.is_multi_sheet,
                    rx.vstack(
                        rx.text("Multiple sheets detected. Select one:", weight="bold"),
                        rx.select(
                            State.sheet_names,
                            placeholder="Choose a sheet...",
                            on_change=State.load_selected_sheet,
                        ),
                        spacing="2",
                        width="100%",
                    )
                ),
                
                rx.upload(
                    rx.vstack(
                        rx.button("Select File", color="white", bg="blue.500"),
                        rx.text("Drag and drop files here or click to select"),
                    ),
                    id="upload1",
                    border="1px dotted rgb(107,99,246)",
                    padding="2em",
                ),
                rx.button(
                    "Upload",
                    on_click=State.handle_upload(rx.upload_files(upload_id="upload1")),
                ),
                rx.button(
                    "Load Sample Data",
                    on_click=State.load_sample_data,
                    variant="soft",
                ),
                spacing="4",
            ),
            width="100%",
        ),
        
        spacing="6",
        width="100%",
    )

def dashboard():
    return require_auth(dashboard_content())
