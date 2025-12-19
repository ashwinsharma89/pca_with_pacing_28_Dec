import reflex as rx
from ..state import State
from ..components.layout import require_auth


def reporting_content():
    """Reporting wizard with template upload, data source selection, preview, mapping, and generation."""
    return rx.vstack(
        rx.heading("📊 Automated Reporting", size="8"),
        # Step 0: Choose data source
        rx.select(
            ["Upload File", "Snowflake", "Databricks", "BigQuery", "S3"],
            placeholder="Select data source",
            value=State.data_source_type,
            on_change=State.set_data_source_type,
        ),
        # Conditional UI based on source type
        rx.cond(
            State.data_source_type == "Upload File",
            # Upload component for CSV/XLSX data file
            rx.upload(
                accept=".csv,.xlsx",
                multiple=False,
                on_drop=State.handle_data_upload,
                max_files=1,
                description="Upload your data file (CSV or XLSX)"
            ),
            # Placeholder for external sources
            rx.callout(
                "External data source integration (Snowflake, Databricks, BigQuery, S3) will be available soon.",
                icon="info"
            ),
        ),
        # Preview of uploaded data (if available)
        rx.cond(
            State.data_structure.get("preview"),
            rx.vstack(
                rx.text("Data Preview:"),
                rx.data_table(
                    data=State.data_structure["preview"],
                    pagination=True,
                    search=True,
                    sort=True,
                ),
                spacing="2"
            ),
            rx.box()
        ),
        # Template upload (existing)
        rx.upload(
            accept=".xlsx",
            multiple=False,
            on_drop=State.handle_template_upload,
            max_files=1,
            description="Upload report template (XLSX)"
        ),
        # Mapping placeholder
        rx.text("Mapping UI will be added here after data and template are ready."),
        # Generate report button
        rx.button(
            "Generate Report",
            on_click=State.generate_report,
            disabled=State.is_generating,
            color_scheme="green",
        ),
        # Show generated report link when ready
        rx.cond(
            State.generated_report_path,
            rx.link(
                "Download Report",
                href=State.generated_report_path,
                download=True,
                color_scheme="blue"
            ),
            rx.box()
        ),
        width="100%",
        spacing="4",
    )


def reporting_page():
    return require_auth(reporting_content())
