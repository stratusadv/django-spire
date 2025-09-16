from __future__ import annotations

from dataclasses import dataclass
from typing_extensions import ClassVar

from django_spire.theme.enums import ThemeFamily, ThemeMode


@dataclass(frozen=True)
class Theme:
    family: ThemeFamily
    mode: ThemeMode

    DEFAULT_FAMILY: ClassVar[ThemeFamily] = ThemeFamily.DEFAULT
    DEFAULT_MODE: ClassVar[ThemeMode] = ThemeMode.LIGHT
    SEPARATOR: ClassVar[str] = '-'

    FAMILY_DISPLAY_NAMES: ClassVar[dict[ThemeFamily, str]] = {
        ThemeFamily.AYU: 'Ayu',
        ThemeFamily.CATPPUCCIN: 'Catppuccin',
        ThemeFamily.DEFAULT: 'Default',
        ThemeFamily.DRACULA: 'Dracula',
        ThemeFamily.GRUVBOX: 'Gruvbox',
        ThemeFamily.MATERIAL: 'Material',
        ThemeFamily.NORD: 'Nord',
        ThemeFamily.OCEANIC_NEXT: 'Oceanic Next',
        ThemeFamily.ONE_DARK: 'One Dark Pro',
        ThemeFamily.PALENIGHT: 'Palenight',
        ThemeFamily.ROSE_PINE: 'Rose Pine',
        ThemeFamily.SYNTHWAVE: 'Synthwave',
        ThemeFamily.TOKYO_NIGHT: 'Tokyo Night',
    }

    def __post_init__(self):
        if isinstance(self.family, str):
            self._validate_family(self.family)

            object.__setattr__(
                self,
                'family',
                ThemeFamily(self.family)
            )

        if isinstance(self.mode, str):
            self._validate_mode(self.mode)

            object.__setattr__(
                self,
                'mode',
                ThemeMode(self.mode)
            )

    @classmethod
    def _parse(cls, theme: str) -> tuple[str, str]:
        parts = theme.strip().split(cls.SEPARATOR)

        if len(parts) < 2:
            message = f'Invalid theme format: {theme}'
            raise ValueError(message)

        mode = parts[-1]
        family = cls.SEPARATOR.join(parts[:-1])

        return family, mode

    @classmethod
    def _validate_family(cls, family: str) -> None:
        if family not in [family.value for family in ThemeFamily]:
            message = f'Invalid theme family: {family}'
            raise ValueError(message)

    @classmethod
    def _validate_mode(cls, mode: str) -> None:
        if mode not in [mode.value for mode in ThemeMode]:
            message = f'Invalid theme mode: {mode}'
            raise ValueError(message)

    @classmethod
    def _validate(cls, family: str, mode: str) -> None:
        cls._validate_family(family)
        cls._validate_mode(mode)

    @classmethod
    def from_string(cls, theme: str, default: Theme | None = None) -> Theme:
        if not theme:
            if default:
                return default

            return cls.get_default()

        try:
            family, mode = cls._parse(theme)
            cls._validate(family, mode)
            return cls(family=ThemeFamily(family), mode=ThemeMode(mode))
        except ValueError:
            if default:
                return default

            raise

    @classmethod
    def get_available(cls) -> list[Theme]:
        return [
            cls(family=family, mode=mode)
            for family in ThemeFamily
            for mode in ThemeMode
        ]

    @classmethod
    def get_default(cls) -> Theme:
        return cls(family=cls.DEFAULT_FAMILY, mode=cls.DEFAULT_MODE)

    @property
    def display(self) -> str:
        family = self.FAMILY_DISPLAY_NAMES.get(self.family, self.family.value)
        mode = self.mode.value.capitalize()
        return f'{family} - {mode}'

    @property
    def family_display(self) -> str:
        return self.FAMILY_DISPLAY_NAMES.get(self.family, self.family.value)

    @property
    def is_dark(self) -> bool:
        return self.mode == ThemeMode.DARK

    @property
    def stylesheet(self) -> str:
        return f'django_spire/css/themes/{self.family.value}/app-{self.mode.value}.css'

    @property
    def value(self) -> str:
        return f'{self.family.value}{self.SEPARATOR}{self.mode.value}'

    def to_dict(self) -> dict:
        return {
            'display': self.display,
            'family': self.family.value,
            'family_display': self.family_display,
            'full': self.value,
            'is_dark': self.is_dark,
            'mode': self.mode.value,
            'stylesheet': self.stylesheet,
        }
