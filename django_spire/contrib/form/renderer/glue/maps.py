from django import forms

from django_spire.contrib.form.field_renderer.glue import field_renderer

DJANGO_FIELD_TO_GLUE_FIELD_RENDERER_MAP = {
    forms.BooleanField: field_renderer.SpireGlueBooleanFieldRenderer,
    forms.CharField: field_renderer.SpireGlueCharFieldRenderer,
    forms.DateField: field_renderer.SpireGlueDateFieldRenderer,
    forms.DateTimeField: field_renderer.SpireGlueDateFieldRenderer,
    forms.IntegerField: field_renderer.SpireGlueIntegerFieldRenderer,
    forms.DecimalField: field_renderer.GlueDecimalFieldRenderer,
    forms.ChoiceField: field_renderer.SpireGlueChoiceFieldRenderer
    # add missing TextField
}