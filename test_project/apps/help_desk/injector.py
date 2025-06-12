from django_spire.auth.group.decorators import permission_required
from django_spire.core.injection.decorator_injector import \
    DecoratorInjector
from django_spire.core.injection.url_injector import UrlConfInjector
from django_spire.help_desk.views.form_views import (
    ticket_delete_form_view,
    ticket_update_form_view,
)


help_desk_url_injector = UrlConfInjector(
    child_injectors=(
        DecoratorInjector(
            decorators=permission_required('django_spire_help_desk.delete_helpdeskticket'),
            injector_target=ticket_delete_form_view
        ),
        DecoratorInjector(
            decorators=permission_required('django_spire_help_desk.change_helpdeskticket'),
            injector_target=ticket_update_form_view
        )
    )
)