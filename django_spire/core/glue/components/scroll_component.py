from abc import abstractmethod, ABC

from django_glue import Glue


class BaseScrollComponent(Glue.Component, ABC):
    template = 'glue/components/scroll_component.html'

    item_updated = Glue.event()

    @abstractmethod
    @Glue.attr
    def get_items(self, reset: bool = False):
        raise NotImplementedError

    @Glue.attr
    def reset_items(self):
        return self.get_items(True)

    @Glue.attr
    def on_item_updated(self, *updated_item_event_kwargs):
        return None

    @Glue.property
    def has_more(self):
        return False
