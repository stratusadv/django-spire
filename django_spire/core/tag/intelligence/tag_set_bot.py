from __future__ import annotations

from dandy import Bot, Prompt, BaseListIntel
from django.utils.text import slugify


class TagsIntel(BaseListIntel[list[str]]):
    tags: list[str]


class TagSetBot(Bot):
    role = 'Tag Identifier'
    task = 'Read through the provided content and return a list of tags.'
    guidelines = (
        Prompt()
        .list([
            'Make sure to have enough tags to properly cover all the provided content.',
            'Include tags that help searchability.',
            'Focus on tagging the words in the content.',
            'Only add additional words that are very relevant to the content.',
            'Use spaces to separate words in tags.',
            'Include common acronyms in addition to the tags.',
        ])
    )

    def process(self, content: Prompt | str) -> set[str]:
        tags_intel = self.llm.prompt_to_intel(
            prompt=(
                Prompt()
                .heading('Content to be Tagged:')
                .line_break()
                .text(content)
            ),
            intel_class=TagsIntel
        )

        for tag in tags_intel:
            word_segments = tag.split(" ")

            if len(word_segments) > 1:
                for word_segment in word_segments:
                    tags_intel.append(word_segment)

        return {slugify(tag) for tag in tags_intel}
