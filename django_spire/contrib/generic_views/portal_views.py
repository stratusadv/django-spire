from __future__ import annotations

from typing_extensions import Any, Callable, TYPE_CHECKING

from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

from django_spire.contrib.breadcrumb.breadcrumbs import Breadcrumbs
from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


# Takes breadcrumb as parameter and returns None
BreadCrumbCallable = Callable[[Breadcrumbs], None]


def detail_view(
    request: WSGIRequest,
    *,
    context_data: dict | None = None,
    breadcrumbs_func: BreadCrumbCallable | None = None,
    obj,
    template: str
) -> TemplateResponse:
    if context_data is None:
        context_data = {}

    breadcrumbs = Breadcrumbs()

    if breadcrumbs_func is None:
        breadcrumbs.add_obj_breadcrumbs(obj)
    else:
        breadcrumbs_func(breadcrumbs)

    base_context_data = {
        'page_title': obj._meta.model._meta.verbose_name,
        'page_description': obj.__str__(),
        'breadcrumbs': breadcrumbs
    }

    context_data = {**base_context_data, **context_data}

    return TemplateResponse(
        request,
        template=template,
        context=context_data
    )


def delete_form_view(
    request: WSGIRequest,
    *,
    context_data: dict | None = None,
    obj,
    activity_func: callable | None = None,
    auto_add_activity: bool = True,
    breadcrumbs_func: BreadCrumbCallable | None = None,
    delete_func: callable | None = None,
    # Present and past tense of verb
    verbs: tuple[str, str] = ('delete', 'deleted'),
    return_url: str,
    template: str = 'django_spire/page/delete_form_page.html'
) -> HttpResponseRedirect | TemplateResponse:
    if context_data is None:
        context_data = {}

    model_name = obj._meta.model._meta.verbose_name

    if request.method == 'POST':
        form = DeleteConfirmationForm(request.POST, obj=obj)

        if form.is_valid():
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
                    device=request.device,
                    information=f'{request.user.get_full_name()} {verbs[1].lower()} {model_name} "{obj}".'
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

    return TemplateResponse(
        request,
        template=template,
        context=context_data
    )


def infinite_scrolling_view(
    request: WSGIRequest,
    *,
    context_data: dict[str, Any],
    queryset: QuerySet | list,
    queryset_name: str,
    template: str
) -> TemplateResponse:
    if context_data is None:
        context_data = {}

    current_page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))

    start = (current_page - 1) * page_size
    end = start + page_size

    object_list = queryset[start:end]

    length = (
        queryset.count()
        if isinstance(queryset, QuerySet)
        else len(queryset)
    )

    has_next = end < length

    base_context_data = {
        'current_page': current_page,
        'has_next': has_next,
        'page_size': page_size,
        queryset_name: object_list
    }

    context_data.update(base_context_data)

    return TemplateResponse(
        request,
        context=context_data,
        template=template
    )


def list_view(
    request: WSGIRequest,
    *,
    context_data: dict | None = None,
    breadcrumbs_func: BreadCrumbCallable | None = None,
    model,
    template: str
) -> TemplateResponse:

    if context_data is None:
        context_data = {}

    breadcrumbs = Breadcrumbs()

    if breadcrumbs_func is None:
        breadcrumbs.add_breadcrumb(name=f'{model._meta.verbose_name} List')
    else:
        breadcrumbs_func(breadcrumbs)

    base_context_data = {
        'page_title': model._meta.verbose_name,
        'page_description': 'List View',
        'breadcrumbs': breadcrumbs
    }

    context_data = {**base_context_data, **context_data}

    return TemplateResponse(
        request,
        template=template,
        context=context_data
    )


def form_view(
    request: WSGIRequest,
    *,
    form,
    context_data: dict | None = None,
    obj,
    breadcrumbs_func: BreadCrumbCallable | None = None,
    verb: str | None = None,
    template: str = 'django_spire/page/form_full_page.html'
) -> TemplateResponse:

    if context_data is None:
        context_data = {}

    model = obj._meta.model

    breadcrumbs = Breadcrumbs()

    if breadcrumbs_func is None:
        breadcrumbs.add_form_breadcrumbs(obj=obj)
    else:
        breadcrumbs_func(breadcrumbs)

    if verb is None:
        verb = 'Edit' if obj.pk else 'Create'

    if obj.pk:
        form_title = f'{verb.title()} {model._meta.verbose_name} {obj}'
        form_description = f'Are you sure you would like to {verb} {model._meta.verbose_name} "{obj}"?'
    else:
        form_title = f'{verb} {model._meta.verbose_name}'
        form_description = ''

    base_context_data = {
        'page_title': model._meta.verbose_name,
        'page_description': f'{verb} {obj}'.title(),
        'breadcrumbs': breadcrumbs,
        'form': form,
        'form_title': form_title,
        'form_description': form_description,
    }

    context_data = {**base_context_data, **context_data}

    return TemplateResponse(request, template, context=context_data)


def model_form_view(
    request: WSGIRequest,
    *,
    form,
    context_data: dict | None = None,
    obj,
    breadcrumbs_func: BreadCrumbCallable | None = None,
    verb: str | None = None,
    template: str = 'django_spire/page/form_full_page.html'
) -> TemplateResponse:
    if breadcrumbs_func is None:
        def breadcrumbs_func(crumbs: Breadcrumbs) -> None:
            if obj.pk is None:
                crumbs.add_form_breadcrumbs(obj)
            else:
                crumbs.add_form_breadcrumbs(obj)

    return form_view(
        request,
        form=form,
        context_data=context_data,
        obj=obj,
        breadcrumbs_func=breadcrumbs_func,
        verb=verb,
        template=template
    )


def template_view(
    request: WSGIRequest,
    page_title: str,
    page_description: str,
    breadcrumbs: Breadcrumbs,
    template: str,
    context_data: dict | None = None
) -> TemplateResponse:
    if context_data is None:
        context_data = {}

    base_context_data = {
        'page_title': page_title,
        'page_description': page_description,
        'breadcrumbs': breadcrumbs
    }
    context_data = {**base_context_data, **context_data}

    return TemplateResponse(request, template, context=context_data)
