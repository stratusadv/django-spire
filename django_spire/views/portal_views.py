from typing import Optional, Callable

from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

from django_spire.breadcrumbs.models import Breadcrumbs
from django_spire.forms.confirmation_forms import DeleteConfirmationForm


# Takes breadcrumb as parameter and returns None
BreadCrumbCallable = Callable[[Breadcrumbs], None]


def detail_view(
        request,
        *,
        context_data: Optional[dict] = None,
        breadcrumbs_func: Optional[BreadCrumbCallable] = None,
        obj,
        template: str
):
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
        request,
        *,
        context_data: Optional[dict] = None,
        obj,
        activity_func: Optional[Callable] = None,
        auto_add_activity: bool = True,
        breadcrumbs_func: Optional[BreadCrumbCallable] = None,
        delete_func: Optional[Callable] = None,
        verbs: tuple[str, str] = ('delete', 'deleted'),  # Present and past tense of verb
        return_url: str,
        template: str = 'spire/page/form_full_page.html'
):
    if context_data is None:
        context_data = {}

    model_name = obj._meta.model._meta.verbose_name

    if request.method == 'POST':
        form = DeleteConfirmationForm(request.POST)
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
        form = DeleteConfirmationForm()

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


def list_view(
        request,
        *,
        context_data: Optional[dict] = None,
        breadcrumbs_func: Optional[BreadCrumbCallable] = None,
        model,
        template: str
):

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
        request,
        *,
        form,
        context_data: Optional[dict] = None,
        obj,
        breadcrumbs_func: Optional[BreadCrumbCallable] = None,
        verb: Optional['str'] = None,
        template: str = 'spire/page/form_full_page.html'
):

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
        request,
        *,
        form,
        context_data: Optional[dict] = None,
        obj,
        breadcrumbs_func: Optional[BreadCrumbCallable] = None,
        verb: Optional['str'] = None,
        template: str = 'spire/page/form_full_page.html'
):

    if breadcrumbs_func is None:
        def breadcrumbs_func(crumbs: Breadcrumbs):
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
        request,
        page_title: str,
        page_description: str,
        breadcrumbs: Breadcrumbs,
        template: str,
        context_data: Optional[dict] = None,
):
    if context_data is None:
        context_data = {}

    base_context_data = {
        'page_title': page_title,
        'page_description': page_description,
        'breadcrumbs': breadcrumbs
    }
    context_data = {**base_context_data, **context_data}

    return TemplateResponse(request, template, context=context_data)
