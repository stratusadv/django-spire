from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.core.redirect.safe_redirect import safe_redirect_url
from django_spire.core.shortcuts import get_object_or_null_obj
from django_spire.form.utils import show_form_errors
from django_spire.history.utils import add_form_activity
from django_spire.views import modal_views, portal_views

import django_glue as dg

from module import forms, models


if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('spireparentapp.delete_spirepermission')
def spireparentapp_spirechildapp_delete_form_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    spirechildapp = get_object_or_404(models.SpireChildApp, pk=pk)

    form_action = reverse(
        'spireparentapp:spirechildapp:delete_form_modal',
        kwargs={'pk': pk}
    )

    def add_activity() -> None:
        spirechildapp.add_activity(
            user=request.user,
            verb='deleted',
            device=request.device,
            information=f'{request.user.get_full_name()} deleted a spirechildapp on "{spirechildapp.spireparentapp}".'
        )

    fallback = reverse(
        'spireparentapp:detail',
        kwargs={'pk': spirechildapp.spireparentapp.pk}
    )

    return_url = safe_redirect_url(request, fallback=fallback)

    return modal_views.dispatch_modal_delete_form_content(
        request,
        obj=spirechildapp,
        form_action=form_action,
        activity_func=add_activity,
        return_url=return_url,
    )


@permission_required('spireparentapp.delete_spirepermission')
def spireparentapp_spirechildapp_delete_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    spirechildapp = get_object_or_404(models.SpireChildApp, pk=pk)

    return_url = request.GET.get(
        'return_url',
        reverse('spirechildapp:page:list')
    )

    return portal_views.delete_form_view(
        request,
        obj=spirechildapp,
        return_url=return_url
    )


@permission_required('spireparentapp.view_spirepermission')
def spireparentapp_spirechildapp_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    spirechildapp = get_object_or_404(models.SpireChildApp, pk=pk)

    context_data = {
        'spirechildapp': spirechildapp,
    }

    return portal_views.detail_view(
        request,
        obj=spirechildapp,
        context_data=context_data,
        template='spirechildapp/page/spirechildapp_detail_page.html'
    )


@permission_required('spireparentapp.change_spirepermission')
def spireparentapp_spirechildapp_form_content_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    spirechildapp = get_object_or_404(models.SpireChildApp, pk=pk)

    dg.glue_model_object(request, 'spirechildapp', spirechildapp)

    context_data = {
        'spirechildapp': spirechildapp
    }

    return TemplateResponse(
        request,
        context=context_data,
        template='spirechildapp/modal/content/spirechildapp_form_modal_content.html'
    )


@permission_required('spireparentapp.change_spirepermission')
def spireparentapp_spirechildapp_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    spirechildapp = get_object_or_null_obj(models.SpireChildApp, pk=pk)

    dg.glue_model_object(request, 'spirechildapp', spirechildapp, 'view')

    if request.method == 'POST':
        form = forms.PlaceholderForm(request.POST, instance=spirechildapp)

        if form.is_valid():
            spirechildapp = form.save()
            add_form_activity(spirechildapp, pk, request.user)

            return redirect(
                request.GET.get(
                    'return_url',
                    reverse('spirechildapp:page:list')
                )
            )

        show_form_errors(request, form)
    else:
        form = forms.PlaceholderForm(instance=spirechildapp)

    return portal_views.form_view(
        request,
        form=form,
        obj=spirechildapp,
        template='spirechildapp/page/spirechildapp_form_page.html'
    )


@permission_required('spireparentapp.view_spirepermission')
def spireparentapp_spirechildapp_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'spirechildapps': models.SpireChildApp.objects.all()
    }

    return portal_views.list_view(
        request,
        model=models.SpireChildApp,
        context_data=context_data,
        template='spirechildapp/page/spirechildapp_list_page.html'
    )
