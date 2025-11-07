from __future__ import annotations


from pydantic import model_validator, BaseModel

from django_spire.knowledge.entry.version.block.constants import SPACES_PER_INDENT
from django_spire.knowledge.entry.version.block.data.data import BaseEditorJsBlockData
from django_spire.knowledge.entry.version.block.data.list.meta import ChecklistItemMeta, \
    OrderedListItemMeta
from django_spire.knowledge.entry.version.block.data.list.choices import \
    ListEditorBlockDataStyle


class ListEditorBlockData(BaseEditorJsBlockData):
    style: ListEditorBlockDataStyle | str
    meta: ChecklistItemMeta | OrderedListItemMeta | None = None
    items: list[ListItemEditorBlockData]

    def render_to_text(self) -> str:
        render_string = ''
        for i, item in enumerate(self.items):
            render_string += item.render_to_text(self.style, 0, i)

        return render_string

    @model_validator(mode='before')
    @classmethod
    def validate_meta(cls, values: dict) -> dict:
        values['style'] = ListEditorBlockDataStyle(values.get('style'))

        if values['style'] == ListEditorBlockDataStyle.ORDERED and 'meta' in values:
            values['meta'] = OrderedListItemMeta(**values['meta'])

        for item in values['items']:
            item = ListItemEditorBlockData.style_aware_create_from_dict(item, values['style'])

        return values


class ListItemEditorBlockData(BaseModel):
    content: str
    meta: ChecklistItemMeta | OrderedListItemMeta | dict | None = None
    items: list[ListItemEditorBlockData] | None = []

    def get_prefix(
            self,
            style: ListEditorBlockDataStyle,
            indent_level: int,
            index = None
    ):
        prefix = ' ' * indent_level * SPACES_PER_INDENT

        if style == ListEditorBlockDataStyle.ORDERED:
            index = index or 0
            start = self.meta.start or 1
            prefix += f'{start + index}.'

        elif style == ListEditorBlockDataStyle.CHECKLIST:
            prefix += f'[{"X" if self.meta.checked else " "}]'

        else:
            prefix += '-'

        return prefix

    def render_to_text(
        self,
        style: ListEditorBlockDataStyle,
        indent_level: int,
        index: int
    ) -> str:
        from django_spire.knowledge.entry.version.converters.markdown_converter import \
            MarkdownConverter

        prefix = self.get_prefix(style, indent_level, index)
        parsed_content = MarkdownConverter.html_to_markdown(self.content)
        render_string = f'{prefix} {parsed_content}\n'
        for i, item in enumerate(self.items):
            render_string += item.render_to_text(style, indent_level + 1, i)

        return render_string

    @classmethod
    def style_aware_create_from_dict(
        cls,
        values: dict,
        style: ListEditorBlockDataStyle
    ) -> ListItemEditorBlockData:
        from django_spire.knowledge.entry.version.block.data.list.maps import \
            LIST_BLOCK_DATA_META_MAP

        if 'meta' in values:
            meta_type = LIST_BLOCK_DATA_META_MAP[style]

            if isinstance(values['meta'], dict):
                values['meta'] = meta_type(**values['meta']) if meta_type else None

        for item in values['items']:
            item = ListItemEditorBlockData.style_aware_create_from_dict(item, style)

        return ListItemEditorBlockData(**values)
