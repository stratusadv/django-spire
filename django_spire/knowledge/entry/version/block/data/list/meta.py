from __future__ import annotations

from pydantic import BaseModel

from django_spire.knowledge.entry.version.block.data.list.choices import \
    OrderedListCounterType


class ChecklistItemMeta(BaseModel):
    checked: bool = False


class OrderedListItemMeta(BaseModel):
    start: int | None = None
    counterType: OrderedListCounterType | str | None = None
