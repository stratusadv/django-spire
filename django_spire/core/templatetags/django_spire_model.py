from django import template
from django.db.models import Model

register = template.Library()


@register.filter
def model_app_label(model_obj: Model) -> str:
    """
    Return the Django app label for the given model instance.

    Args:
        model_obj: A Django model instance.

    Returns:
        The app label defined by the model's app configuration.
    """

    return model_obj._meta.app_label


@register.filter
def model_name(model_obj: Model) -> str:
    """
    Return the Django model name for the given model instance.

    Args:
        model_obj: A Django model instance.

    Returns:
        The model name (lowercased) as defined by Django's model metadata.
    """

    return model_obj._meta.model_name
