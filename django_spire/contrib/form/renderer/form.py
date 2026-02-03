from django.forms import forms

from django_spire.contrib.form.renderer.glue.factories import \
    create_glue_renderer_from_django_field


class BaseFormRenderer:
    def __init__(self, form: forms.Form):
        self.form = form
        self.renderers = {
            field_name: create_glue_renderer_from_django_field(
                field_name=field_name,
                field=field,
                value=form.cleaned_data.get(field_name, field.initial)
            )
            for field_name, field in form.fields.items()
        }

    def render_js(self) -> str:
        return ''.join([renderer.render_js() for renderer in self.renderers.values()])

    def render_field_js(self, field_name: str, **kwargs) -> str:
        renderer = self.renderers.get(field_name)
        if not renderer:
            return ''

        return renderer.render_js(**kwargs)
