from dandy import Prompt
from django.forms import model_to_dict

from django_spire.ai.context.models import Organization


def organization_info_prompt() -> Prompt:
    org_dict = model_to_dict(Organization.objects.get_only(), exclude=[
        'id', 'created_datetime', 'is_active', 'is_deleted'
    ])

    return (
        Prompt()
        .heading('Organization Information')
        .dict(org_dict)
    )
