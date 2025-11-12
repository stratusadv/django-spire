from __future__ import annotations

from enum import StrEnum


class ThemeFamily(StrEnum):
    AYU = 'ayu'
    CATPPUCCIN = 'catppuccin'
    DEFAULT = 'default'
    GRUVBOX = 'gruvbox'
    MATERIAL = 'material'
    NORD = 'nord'
    ONE_DARK = 'one-dark'
    PALENIGHT = 'palenight'
    ROSE_PINE = 'rose-pine'
    TOKYO_NIGHT = 'tokyo-night'


class ThemeMode(StrEnum):
    DARK = 'dark'
    LIGHT = 'light'
