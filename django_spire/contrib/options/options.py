from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Option:
    key: str
    value: str | bool | int


@dataclass
class OptionSection:
    name: str
    options: list[Option] = field(default_factory=list)

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()

    def __contains__(self, option_key: str) -> bool:
        return any(option.key == option_key for option in self.options)

    def __getitem__(self, option_key: str) -> Option:
        for option in self.options:
            if option.key.lower() == option_key.lower():
                return option

        message = f'Option "{option_key}" not found'
        raise KeyError(message)

    def to_dict(self):
        section_dict = {}

        for option in self.options:
            section_dict[option.key.lower()] = option.value

        return section_dict


@dataclass
class Options:
    sections: list[OptionSection] = field(default=list)

    def __eq__(self, other):
        # Compares the section names and option keys to sync options.
        section_names = sorted([section.name.lower() for section in self.sections])
        other_section_names = sorted([section.name.lower() for section in other.sections])

        if section_names != other_section_names:
            return False

        for section in self.sections:
            option_keys = sorted([option.key.lower() for option in section.options])
            other_option_keys = sorted([option.key.lower() for option in other[section.name].options])

            if option_keys != other_option_keys:
                return False

        return True

    def __contains__(self, section_name: str) -> bool:
        return any(section.name == section_name for section in self.sections)

    def __getitem__(self, section_name: str) -> OptionSection:
        for section in self.sections:
            if section.name.lower() == section_name.lower():
                return section

        message = f'Section "{section_name}" not found'
        raise KeyError(message)

    @classmethod
    def load_dict(cls, options_dict: dict):
        sections = []

        for section_name, section_options in options_dict.items():
            options = []

            for option_key, option_value in section_options.items():
                options.append(Option(key=option_key, value=option_value))

            sections.append(OptionSection(name=section_name, options=options))

        return cls(sections=sections)

    def get_setting(self, section_name: str, option_key: str):
        return self[section_name][option_key].value

    def sync_options(self, default_options: 'Options'):
        new_sections = []
        for section in default_options.sections:
            new_section = OptionSection(name=section.name)

            for option in section.options:
                key = option.key
                if section.name in self and key in self[section.name]:
                    value = self[section.name][key].value
                else:
                    value = option.value

                new_section.options.append(Option(key=key, value=value))

            new_sections.append(new_section)

        self.sections = new_sections

    def update_setting(self, section_name: str, option_key: str, value: str | bool):
        self[section_name][option_key].value = value

    def to_dict(self):
        options_dict = {}

        for section in self.sections:
            options_dict[section.name.lower()] = section.to_dict()

        return options_dict
