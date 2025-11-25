from __future__ import annotations

from enum import StrEnum


class ResponsiveMode(StrEnum):
    """
    It defines how tables handle responsive behavior at different viewport sizes.

    Collapse: Any columns with breakpoint attributes are hidden at smaller viewports
        and shown at their specified breakpoint.

    Scroll: All columns remain visible regardless of viewport size. The table
        container enables horizontal scrolling to accommodate the full width.
    """

    COLLAPSE = 'collapse'
    SCROLL = 'scroll'
