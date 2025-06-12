from django_spire.help_desk.permissions import HelpDeskTicketPermissionController
from django_spire.help_desk.urls.shortcuts import include_helpdesk_urls_with_permissions

app_name = 'help_desk'

urlpatterns = include_helpdesk_urls_with_permissions(
    permission_controller=HelpDeskTicketPermissionController,
)