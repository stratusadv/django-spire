from dandy import Bot, Prompt, BaseListIntel


class TagsIntel(BaseListIntel[list[str]]):
    tags: list[str]


class TagSetBot(Bot):
    llm_role = 'Tag Identifier'
    llm_task = 'Read through the provided content and return a list of tags.'
    llm_guidelines = (
        Prompt()
        .list([
            'Make sure to have enough tags to properly cover all the provided content.',
            'Include known acronyms along with the full tags.',
        ])
    )

    def process(self, content: str) -> set[str]:
        tags_intel = self.llm.prompt_to_intel(
            prompt=content,
            intel_class=TagsIntel
        )

        for tag in tags_intel:
            word_segments = tag.split(" ")

            if len(word_segments) > 1:
                for word_segment in word_segments:
                    tags_intel.append(word_segment)

        return {tag.lower() for tag in tags_intel}
