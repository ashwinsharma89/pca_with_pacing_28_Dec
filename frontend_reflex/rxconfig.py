import reflex as rx

config = rx.Config(
    app_name="frontend_reflex",
    api_url="http://localhost:8000",
    theme=rx.theme(
        appearance="dark",
        accent_color="violet",
        radius="large",
        scaling="110%",
    ),
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)