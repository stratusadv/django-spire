from dandy.llm import BaseLlmBot, Prompt
from dandy.intel import BaseIntel
from dandy.core.cache import cache_to_sqlite

class AttrsIntel(BaseIntel):
    items: list[str]


class SeedingAttrsLlmBot(BaseLlmBot):
    config = 'SEEDING_ATTR_LLM_BOT'

    @classmethod
    @cache_to_sqlite('seeding')
    def process(cls, attr_type: type, description: str, count: int) -> Any:
        attrs_intel = cls.process_prompt_to_intel(
            prompt=(
                Prompt()
                .text(f'Create {count} {description}')
            ),
            intel_class=AttrsIntel
        )

        return [ attr_type(attr) for attr in attrs_intel.items ]

