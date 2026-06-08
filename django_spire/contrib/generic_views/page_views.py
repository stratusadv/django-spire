from __future__ import annotations

from typing import Callable, TYPE_CHECKING

from django.db.models import QuerySet, Model
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm

if TYPE_CHECKING:
    from typing import Any

    from django.core.handlers.wsgi import WSGIRequest
    from django.forms import BaseForm


def delete_form_view(
    request: WSGIRequest,
    *,
    context_data: dict | None = None,
    obj: Model,
    activity_func: Callable[[], None] | None = None,
    auto_add_activity: bool = True,
    breadcrumbs_func: BreadcrumbCallable | None = None,
    delete_func: Callable[[], None] | None = None,
    verbs: tuple[str, str] = ('delete', 'deleted'),
    return_url: str,
    template: str = 'django_spire/page/delete_confirmation_form_page.html',
) -> HttpResponseRedirect | TemplateResponse:
    if context_data is None:
        context_data = {}

    model_name = obj._meta.model._meta.verbose_name

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=obj)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                if delete_func is not None:
                    delete_func()
                else:
                    obj.set_deleted()

                if activity_func is not None:
                    activity_func()
                elif hasattr(obj, 'add_activity') and auto_add_activity:
                    obj.add_activity(
                        user=request.user,
                        verb=verbs[1],
                        information=f'{request.user.get_full_name()} {verbs[1].lower()} {model_name} "{obj}".',
                    )

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=obj)

    breadcrumbs = Breadcrumbs()

    if breadcrumbs_func is None:
        breadcrumbs.add_obj_breadcrumbs(obj)
        breadcrumbs.add_breadcrumb(name=verbs[0].title())
    else:
        breadcrumbs_func(breadcrumbs)

    base_context_data = {
        'page_title': obj.__str__(),
        'page_description': verbs[0].title(),
        'breadcrumbs': breadcrumbs,
        'form': form,
        'form_title': f'{verbs[0].title()} {obj}',
        'form_description': f'Are you sure you would like to {verbs[0].lower()} {model_name} "{obj}"?',
    }

    context_data = {**base_context_data, **context_data}

    return TemplateResponse(request, template=template, context=context_data)


def form_view(
    request: WSGIRequest,
    *,
    form: BaseForm,
    context_data: dict | None = None,
    obj: Model,
    verb: str | None = None,
    template: str = 'django_spire/page/form_full_page.html',
) -> TemplateResponse:

    if context_data is None:
        context_data = {}

    model = obj._meta.model

    if verb is None:
        verb = 'Edit' if obj.pk else 'Create'

    if obj.pk:
        form_title = f'{verb.title()} {model._meta.verbose_name} {obj}'
        form_description = (
            f'Are you sure you would like to {verb} {model._meta.verbose_name} "{obj}"?'
        )
    else:
        form_title = f'{verb} {model._meta.verbose_name}'
        form_description = ''

    base_context_data = {
        'page_title': model._meta.verbose_name,
        'page_description': f'{verb} {obj}'.title(),
        'form': form,
        'form_title': form_title,
        'form_description': form_description,
    }

    context_data = {**base_context_data, **context_data}

    return TemplateResponse(request, template, context=context_data)


def model_form_view(
    request: WSGIRequest,
    *,
    form: BaseForm,
    context_data: dict | None = None,
    obj: Model,
    verb: str | None = None,
    template: str = 'django_spire/page/form_full_page.html',
) -> TemplateResponse:

    return form_view(
        request,
        form=form,
        context_data=context_data,
        obj=obj,
        verb=verb,
        template=template,
    )


def template_view(
    request: WSGIRequest,
    page_title: str,
    page_description: str,
    template: str,
    context_data: dict | None = None,
) -> TemplateResponse:
    if context_data is None:
        context_data = {}

    base_context_data = {
        'page_title': page_title,
        'page_description': page_description,
    }

    context_data = {**base_context_data, **context_data}

    return TemplateResponse(request, template, context=context_data)
