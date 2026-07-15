from __future__ import annotations

from typing import Any

from django.utils.timezone import localdate

from dandy import Bot, Prompt, BaseIntel


class LlmFieldSeedingBot(Bot):
    role = 'Data Generation Expert'
    task = 'Create seed data for a software application.'
    guidelines = (
        Prompt()
        .text('ALL FIELDS ARE REQUIRED TO HAVE DATA.')
        .text(
            'Instructions have context behind the meaning of the data and how it should be created.'
        )
        .text(
            f"Today's date is {localdate().strftime('%Y-%m-%d')} use this in context for generating dates and datetimes"
        )
    )

    def process(self, object_name: str, fields_types: dict[str, type]) -> dict[str, Any]:
        fields_values = {}

        # return self.llm.prompt_to_intel(prompt=prompt, intel_class=intel_class)

        return fields_values
