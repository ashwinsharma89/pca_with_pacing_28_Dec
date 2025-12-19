import reflex as rx

# Premium Glassmorphism Styles

glass_style = {
    "background": "rgba(255, 255, 255, 0.05)",
    "backdrop_filter": "blur(10px)",
    "border": "1px solid rgba(255, 255, 255, 0.1)",
    "box_shadow": "0 4px 30px rgba(0, 0, 0, 0.1)",
    "border_radius": "16px",
}

sidebar_style = {
    "background": "rgba(17, 17, 17, 0.8)",
    "backdrop_filter": "blur(20px)",
    "border_right": "1px solid rgba(255, 255, 255, 0.05)",
    "height": "100vh",
}

card_hover_style = {
    "transition": "transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out",
    "_hover": {
        "transform": "translateY(-2px)",
        "box_shadow": "0 8px 30px rgba(0, 0, 0, 0.2)",
        "border": "1px solid rgba(var(--accent-9), 0.5)",
    }
}

# Metric Card Style
metric_card_style = {
    **glass_style,
    **card_hover_style,
    "padding": "20px",
    "display": "flex",
    "flex_direction": "column",
    "justify_content": "space-between",
}
