from django_spire.core.urls.shortcuts import include_app_urls_with_permissions
from django_spire.help_desk.permissions import HelpDeskTicketPermissionController
from django_spire.help_desk.urls.page_urls import urlpatterns as page_urlpatterns
from django_spire.help_desk.urls.form_urls import urlpatterns as form_urlpatterns


def include_helpdesk_urls_with_permissions(
    permission_controller: type[HelpDeskTicketPermissionController] = HelpDeskTicketPermissionController
):
    return include_app_urls_with_permissions(
        app_name='help_desk',
        namespace_url_patterns=[
            ('page', page_urlpatterns),
            ('form', form_urlpatterns),
        ],
        permission_controller=permission_controller,
    )