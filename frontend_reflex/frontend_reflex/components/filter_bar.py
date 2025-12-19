import reflex as rx
from ..state import State

def filter_bar() -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.text("Filters:", weight="bold", size="4"),
            
            # Date Range (Basic implementation with inputs)
            rx.hstack(
                rx.text("Date Range:", size="2"),
                rx.text(
                    f"{State.filter_date_range[0]} - {State.filter_date_range[1]}",
                    size="2",
                    color_scheme="gray"
                ),
               # Advanced date picker requires custom component or just inputs
               # For now, simplest is showing current range. The DataState sets default.
               # Allowing user to change logic:
            ),

            # Multi-Select Platforms
            rx.popover.root(
                rx.popover.trigger(
                    rx.button(
                        rx.hstack(rx.icon("layers"), rx.text("Platforms")),
                        variant="soft", color_scheme="violet"
                    )
                ),
                rx.popover.content(
                    rx.scroll_area(
                        rx.vstack(
                            rx.foreach(
                                State.available_platforms,
                                lambda x: rx.checkbox(
                                    x,
                                    checked=State.selected_platforms.contains(x),
                                    on_change=lambda val: State.toggle_platform(x, val),
                                    size="3"
                                )
                            ),
                            gap="2",
                        ),
                        type="always", scrollbars="vertical", style={"max_height": "300px"}
                    ),
                    width="200px"
                ),
            ),
            
            # Multi-Select Campaigns
            rx.popover.root(
                rx.popover.trigger(
                     rx.button(
                        rx.hstack(rx.icon("megaphone"), rx.text("Campaigns")),
                        variant="soft", color_scheme="blue"
                    )
                ),
                rx.popover.content(
                    rx.scroll_area(
                        rx.vstack(
                            rx.foreach(
                                State.available_campaigns,
                                lambda x: rx.checkbox(
                                    x,
                                    checked=State.selected_campaigns.contains(x),
                                    on_change=lambda val: State.toggle_campaign(x, val),
                                    size="3"
                                )
                            ),
                            gap="2",
                        ),
                        type="always", scrollbars="vertical", style={"max_height": "300px"}
                    ),
                    width="300px"
                ),
            ),
            
            align_items="center",
            spacing="4",
        ),
        size="2",
        width="100%",
        variant="surface"
    )
