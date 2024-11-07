from __future__ import annotations

from django_spire.history.querysets import HistoryQuerySet


class RecipeQuerySet(HistoryQuerySet):
    def by_cookbook(self, pk: int):
        return self.filter(cookbook_recipe__cookbook_id=pk).distinct()


class IngredientQuerySet(HistoryQuerySet):
    pass
