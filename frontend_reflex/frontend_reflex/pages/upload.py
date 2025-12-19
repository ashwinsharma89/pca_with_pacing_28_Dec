import reflex as rx
from ..state.data import DataState
from ..components.sidebar import sidebar_layout

def upload_dropzone() -> rx.Component:
    """Component for drag and drop file upload."""
    return rx.upload(
        rx.vstack(
            rx.button(
                "Select File",
                color="white",
                bg="violet",
                border=f"1px solid {rx.color('gray', 8)}",
            ),
            rx.text(
                "Drag and drop files here or click to select",
                size="4",
                opacity=0.7,
            ),
            rx.text(
                "Supports .csv, .xlsx, .xls",
                size="2",
                opacity=0.5,
            ),
            align="center",
            justify="center",
            spacing="4",
            padding="40px",
            border=f"2px dashed {rx.color('gray', 5)}",
            border_radius="xl",
            background_color="rgba(255, 255, 255, 0.02)",
            width="100%",
            height="250px",
            _hover={
                "border_color": rx.color("violet", 9),
                "background_color": "rgba(255, 255, 255, 0.05)",
            },
        ),
        id="upload1",
        border="0px",
        padding="0px",
        multiple=False,
        accept={
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
            "application/vnd.ms-excel": [".xls"],
            "text/csv": [".csv"]
        },
        max_files=1,
    )

def upload_content() -> rx.Component:
    return rx.vstack(
        rx.heading("Upload Data", size="8", margin_bottom="4"),
        rx.text(
            "Upload your campaign performance data for analysis. Supported formats: CSV, Excel.",
            color="gray",
            margin_bottom="8",
        ),
        
        # Upload Section
        rx.card(
            rx.vstack(
                upload_dropzone(),
                rx.hstack(
                    rx.foreach(
                        rx.selected_files("upload1"),
                        lambda x: rx.text(x, size="2", color=rx.color("violet", 9))
                    ),
                    rx.divider(),
                    rx.button(
                        "Upload and Process",
                        on_click=DataState.handle_upload(rx.upload_files(upload_id="upload1")),
                        size="3",
                        variant="surface",
                        width="100%",
                    ),
                    width="100%",
                    spacing="4",
                ),
                padding="6",
            ),
            width="100%",
        ),
        
        # Data Preview Section (Only shows if rows > 0)
        rx.cond(
            DataState.total_rows > 0,
            rx.vstack(
                rx.heading("Data Preview", size="6", margin_top="8"),
                rx.text(DataState.validation_summary, color="green"),
                rx.data_table(
                    data=DataState.data_preview,
                    columns=DataState.columns,
                    pagination=True,
                    search=True,
                    sort=True,
                    resizable=True,
                ),
                width="100%",
                spacing="4",
                margin_top="8",
            )
        ),

        # Sheet Selection Modal (for multi-sheet Excel)
        rx.cond(
            DataState.is_multi_sheet,
            rx.dialog.root(
                rx.dialog.content(
                    rx.dialog.title("Select Sheet"),
                    rx.dialog.description("Multiple sheets detected. Please select one to analyze."),
                    rx.select(
                        DataState.sheet_names,
                        placeholder="Select a sheet...",
                        on_change=DataState.load_selected_sheet
                    ),
                    rx.dialog.close(
                        rx.button("Cancel", color_scheme="gray", variant="soft"),
                    ),
                ),
                open=DataState.is_multi_sheet,
            )
        ),
        
        width="100%",
        spacing="6",
        padding="8",
        min_height="100vh",
    )

def upload_page() -> rx.Component:
    return sidebar_layout(
        upload_content()
    )
