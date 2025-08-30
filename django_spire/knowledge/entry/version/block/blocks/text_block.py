import re

from django_spire.knowledge.entry.version.block.choices import BlockTypeChoices
from django_spire.knowledge.entry.version.block.blocks.block import BaseBlock


class TextBlock(BaseBlock):
    value: str
    type: BlockTypeChoices = BlockTypeChoices.TEXT
    detail_template: str = 'django_spire/knowledge/entry/version/block/detail/component/text_component.html'
    update_template: str = 'django_spire/knowledge/entry/version/block/update/component/text_component.html'

    def render_to_text(self) -> str:
        return f'{self.value}\n'

    def render_to_html(self) -> str:
        line_break_html = re.sub(r'\n', '<br>', self.value)
        bolded_html = re.sub(
            r'\*\*(.*?)\*\*', r'<span class="fw-bold">\1</span>',
            line_break_html
        )
        italicized_html = re.sub(
            r'\*(.*?)\*', r'<span class="fst-italic">\1</span>',
            bolded_html
        )
        strikethrough_html = re.sub(
            r'~~(.*?)~~', r'<span class="text-decoration-line-through">\1</span>',
            italicized_html
        )

        return strikethrough_html
