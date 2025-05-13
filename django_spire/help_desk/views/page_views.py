from django.template.response import TemplateResponse

from django_spire.help_desk.models import HelpDeskTicket


def ticket_list_view(request):
    tickets = HelpDeskTicket.objects.order_by('-created_datetime').all()

    return TemplateResponse(
        request,
        context = {
            "tickets": tickets
        },
        template = 'django_spire/help_desk/page/ticket_list_page.html'
    )
