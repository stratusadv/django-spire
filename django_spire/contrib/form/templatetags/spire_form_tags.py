from django import template
from django import forms

from django_spire.contrib.form.field_renderer.glue.factories import \
    create_glue_renderer_from_django_field

register = template.Library()


@register.simple_tag
def django_form_to_js_glue_fields(form: forms.Form) -> str:
    field_names_fields_default_values = []

    for field_name, field in form.fields.items():
        if field_name in form.cleaned_data:
            default_value = form.cleaned_data[field_name]
        else:
            default_value = None

        field_names_fields_default_values.append((field_name, field, default_value))

    return ''.join([
        create_glue_renderer_from_django_field(field_name, field).render_js(
            default_value=default_value
        )
        for field_name, field, default_value in field_names_fields_default_values
    ])


@register.simple_tag
def django_field_to_js_glue_field(field_name: str, field: forms.Field, **kwargs) -> str:
    return create_glue_renderer_from_django_field(field_name, field).render_js(**kwargs)


@register.inclusion_tag(template.Template('{% include dynamic_template with glue_field=glue_field glue_model_field=glue_model_field %}'),
                        takes_context=True)
def spire_form_field(context, form, glue_field = None, glue_model_field = None, **kwargs) -> str:
    context.update({
        'dynamic_template': create_glue_renderer_from_django_field(
            glue_model_field or glue_field,
            form.fields[glue_model_field or glue_field],
        ).render_html(**kwargs)
    })

    if glue_field:
        context.update({'glue_field': glue_field})

    if glue_model_field:
        context.update({'glue_model_field': glue_model_field})

    return context