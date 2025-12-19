import reflex as rx
from .state import State
from .pages.dashboard import dashboard
from .pages.analysis import analysis
from .pages.qa import qa_page
from .pages.visualizations import visualizations_page
from .pages.deep_dive import deep_dive_page
from .pages.diagnostics import diagnostics_page
from .pages.predictive import predictive_page
from .pages.reporting import reporting_page
from .pages.reporting import reporting_page
from .pages.settings import settings_page
from .pages.upload import upload_page

# Load styles
style = {
    "font_family": "Inter",
    "background_color": rx.color("gray", 1),
}

app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="violet",
        radius="large",
        scaling="100%",
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap",
        "/styles.css",  # 2x text scaling
    ],
    style={
        "font_family": "Outfit, sans-serif",
        "background_color": "#050510", # Deep dark background
    }
)

# Add pages
app.add_page(dashboard, route="/", title="PCA Agent - Dashboard", on_load=State.check_auth)
app.add_page(analysis, route="/analysis", title="PCA Agent - AI Analysis", on_load=State.check_auth)
app.add_page(deep_dive_page, route="/deep-dive", title="PCA Agent - Deep Dive")
app.add_page(visualizations_page, route="/visualizations", title="Data Visualizations")
app.add_page(qa_page, route="/qa", title="PCA Agent - Q&A")
app.add_page(diagnostics_page, route="/diagnostics", title="PCA Agent - Diagnostics")
app.add_page(predictive_page, route="/predictive", title="PCA Agent - Predictive")
app.add_page(reporting_page, route="/reporting", title="PCA Agent - Reporting")
app.add_page(upload_page, route="/upload", title="PCA Agent - Upload Data")
app.add_page(settings_page, route="/settings", title="PCA Agent - Settings")
