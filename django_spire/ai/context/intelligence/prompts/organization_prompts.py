from __future__ import annotations

from dandy import Prompt
from django.forms import model_to_dict

from django_spire.ai.context.models import Organization


def organization_info_prompt() -> Prompt:
    org = Organization.objects.get_only_or_none()

    if org is None:
        return Prompt().text('There is no organization information available.')

    org_dict = model_to_dict(
        org, exclude=['id', 'created_datetime', 'is_active', 'is_deleted']
    )

    return Prompt().heading('Organization Information').dict(org_dict)
