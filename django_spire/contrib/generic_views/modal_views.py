from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

from django_spire.core.redirect import safe_redirect_url
from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm, ConfirmationForm
from django_spire.contrib.form.utils import show_form_errors

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.db.models import Model


def _dispatch_modal_form_content(
        request: WSGIRequest,
        *,
        obj: Model,
        form_action: str,
        form_class: type,
        context_data: dict | None = None,
        activity_func: callable | None = None,
        auto_add_activity: bool = True,
        verbs: tuple[str, str] = ('', ''),  # Present and past tense of verb
        return_url: str | None = None,
        template: str = '',
        show_success_message: bool = False,
        action_kwargs: dict = {},
) -> HttpResponseRedirect | TemplateResponse:
    if context_data is None:
        context_data = {}

    model_name = obj._meta.model._meta.verbose_name

    if request.method == 'POST':
        form = form_class(request.POST, obj=obj)

        if form.is_valid():
            form.save(
                user=request.user,
                verbs=verbs,
                activity_func=activity_func,
                auto_add_activity=auto_add_activity,
                **action_kwargs,
            )

            if show_success_message:
                messages.success(request, f'Successfully {verbs[1]} {model_name}.')

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


def dispatch_modal_delete_form_content(
        request: WSGIRequest,
        *,
        obj: Model,
        form_action: str,
        context_data: dict | None = None,
        activity_func: callable | None = None,
        auto_add_activity: bool = True,
        delete_func: callable | None = None,
        verbs: tuple[str, str] = ('delete', 'deleted'),
        return_url: str | None = None,
        template: str = 'django_spire/modal/content/dispatch_modal_delete_confirmation_content.html',
        show_success_message: bool = False,
) -> HttpResponseRedirect | TemplateResponse:
    return _dispatch_modal_form_content(
        request,
        obj=obj,
        form_action=form_action,
        form_class=DeleteConfirmationForm,
        context_data=context_data,
        activity_func=activity_func,
        auto_add_activity=auto_add_activity,
        verbs=verbs,
        return_url=return_url,
        template=template,
        show_success_message=show_success_message,
        action_kwargs={
            'delete_func': delete_func,
        }
    )


def dispatch_confirmation_modal_form_content(
        request: WSGIRequest,
        *,
        obj: Model,
        form_action: str,
        context_data: dict | None = None,
        activity_func: callable | None = None,
        auto_add_activity: bool = True,
        confirmation_func: callable | None = None,
        verbs: tuple[str, str] = ('confirm', 'confirmed'),
        return_url: str | None = None,
        template: str = 'django_spire/modal/content/dispatch_modal_confirmation_content.html',
        show_success_message: bool = False,
) -> HttpResponseRedirect | TemplateResponse:
    return _dispatch_modal_form_content(
        request,
        obj=obj,
        form_action=form_action,
        form_class=ConfirmationForm,
        context_data=context_data,
        activity_func=activity_func,
        auto_add_activity=auto_add_activity,
        verbs=verbs,
        return_url=return_url,
        template=template,
        show_success_message=show_success_message,
        action_kwargs={
            'confirmation_func': confirmation_func,
        }
    )
