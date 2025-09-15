from __future__ import annotations

from enum import StrEnum


class ThemeFamily(StrEnum):
    AYU = 'ayu'
    CATPPUCCIN = 'catppuccin'
    DEFAULT = 'default'
    DRACULA = 'dracula'
    GRUVBOX = 'gruvbox'
    MATERIAL = 'material'
    NORD = 'nord'
    OCEANIC_NEXT = 'oceanic-next'
    ONE_DARK = 'one-dark'
    PALENIGHT = 'palenight'
    ROSE_PINE = 'rose-pine'
    SYNTHWAVE = 'synthwave'
    TOKYO_NIGHT = 'tokyo-night'


class ThemeMode(StrEnum):
    DARK = 'dark'
    LIGHT = 'light'
