from typing import Optional, Callable

from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

from django_spire.core.forms import DeleteConfirmationForm
from django_spire.core.redirect import safe_redirect_url
from django_spire.core.forms import show_form_errors


def dispatch_modal_delete_form_content(
        request,
        *,
        obj,
        form_action: str,
        context_data: Optional[dict] = None,
        activity_func: Optional[Callable] = None,
        auto_add_activity: bool = True,
        delete_func: Optional[Callable] = None,
        verbs: tuple[str, str] = ('delete', 'deleted'),  # Present and past tense of verb
        return_url: Optional[str] = None,
        template: str = 'core/modal/content/dispatch_modal_delete_confirmation_content.html'
):
    if context_data is None:
        context_data = {}

    model_name = obj._meta.model._meta.verbose_name

    if request.method == 'POST':
        form = DeleteConfirmationForm(request.POST, obj=obj)
        if form.is_valid():
            form.save(
                user=request.user,
                verbs=verbs,
                delete_func=delete_func,
                activity_func=activity_func,
                auto_add_activity=auto_add_activity
            )

        else:
            show_form_errors(request, form)

        if return_url is None:
            return_url = safe_redirect_url(request)

        return HttpResponseRedirect(return_url)

    base_context_data = {
        'form_title': f'{model_name} - {verbs[0].title()} {obj}',
        'form_action': form_action,
        'form_description': f'Are you sure you would like to {verbs[0].lower()} {model_name} "{obj}"?',
    }

    context_data = {**base_context_data, **context_data}

    return TemplateResponse(
        request,
        template=template,
        context=context_data
    )
