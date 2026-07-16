from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django_glue import Glue

from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.navigation import HelpDeskNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required()
def ticket_list_view(request: WSGIRequest) -> TemplateResponse:
    tickets = HelpDeskTicket.objects.active()

    paginated_tickets = Paginator(tickets.order_by('-created_datetime'), 10).get_page(
        request.GET.get('page', 1)
    )

    Glue.model(request, 'ticket', HelpDeskTicket())
    Glue.queryset(request, 'tickets', tickets, Glue.Access.CHANGE)

    nav = HelpDeskNavigation()
    nav.page_title = 'Ticket'
    nav.page_description = 'List View'
    nav.breadcrumbs.add('Tickets', 'django_spire:help_desk:page:list')
    context = nav.as_context()
    context['tickets'] = paginated_tickets
    context['ticket_count'] = tickets.count()
    return TemplateResponse(
        request=request,
        context=context,
        template='django_spire/help_desk/page/ticket_list_page.html',
    )


@login_required()
def ticket_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    ticket = get_object_or_404(HelpDeskTicket, pk=pk)

    nav = HelpDeskNavigation()
    nav.page_title = str(ticket)
    nav.page_description = 'Detail View'
    nav.breadcrumbs.add('Tickets', 'django_spire:help_desk:page:list')
    nav.breadcrumbs.add(str(ticket))
    context = nav.as_context()
    context['ticket'] = ticket

    return TemplateResponse(
        request, 'django_spire/help_desk/page/ticket_detail_page.html', context=context
    )
