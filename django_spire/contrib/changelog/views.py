from django.template.response import TemplateResponse

from django_spire.contrib.changelog.validators import get_validated_changelog


def changelog_card_content_view(request):
    return TemplateResponse(
        request,
        context={'changelog': get_validated_changelog()},
        template='django_spire/contrib/changelog/content/changelog_content.html',
    )