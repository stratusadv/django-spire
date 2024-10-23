import json

from django.forms import Widget
from django.template import loader
from django.utils.safestring import mark_safe


class TaggingWidget(Widget):
    template_name = 'core/comment/widget/tagging_widget.html'
    user_list = None
    information = None

    def __init__(self, user_list, *args, **kwargs):
        super(TaggingWidget, self).__init__(*args, **kwargs)
        self.user_list = user_list

    def get_context(self, name, value, attrs):
        context_data = super(TaggingWidget, self).get_context(name, value, attrs)
        context_data['user_list'] = json.dumps(self.user_list)
        # context_data['information'] = self.information
        return context_data

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        template = loader.get_template(self.template_name).render(context)
        return mark_safe(template)
