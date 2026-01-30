from __future__ import annotations

from typing import TYPE_CHECKING

import django_glue as dg
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.auth.group.utils import has_app_permission_or_404
from django_spire.comment import models
from django_spire.comment.forms import CommentForm
from django_spire.contrib.form.utils import show_form_errors
from django_spire.contrib.generic_views import dispatch_modal_delete_form_content
from django_spire.core.redirect import safe_redirect_url
from django_spire.core.shortcuts import get_object_or_null_obj, \
    model_object_from_app_label

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required()
def comment_modal_form_content(
    request: WSGIRequest,
    comment_pk: int,
    obj_pk: int,
    app_label: str,
    model_name: str
) -> TemplateResponse:
    has_app_permission_or_404(request.user, app_label, model_name, 'change')

    if comment_pk == 0:
        comment = get_object_or_null_obj(models.Comment, pk=comment_pk)
    else:
        comment = get_object_or_404(models.Comment, pk=comment_pk, user__id=request.user.pk)

    dg.glue_model_object(request, 'comment', comment)

    context_data = {
        'app_label': app_label,
        'model_name': model_name,
        'comment': comment,
        'obj_pk': obj_pk,
    }

    return TemplateResponse(
        request,
        context=context_data,
        template='django_spire/comment/form/comment_form.html',
    )


@login_required()
def comment_form_view(
    request: WSGIRequest,
    comment_pk: int,
    obj_pk: int,
    app_label: str,
    model_name: str
) -> HttpResponseRedirect:
    has_app_permission_or_404(request.user, app_label, model_name, 'change')

    if comment_pk == 0:
        comment = get_object_or_null_obj(models.Comment, pk=comment_pk)
    else:
        comment = get_object_or_404(models.Comment, pk=comment_pk, user__id=request.user.pk)

    obj = model_object_from_app_label(app_label, model_name, obj_pk)

    if not hasattr(obj, 'add_comment'):
        message = f'Object {obj} does not have the comment model mixin.'
        raise Exception(message)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            # TODO: Create comment factory.
            if comment_pk == 0:
                obj.add_comment(
                    user=request.user,
                    information=form.cleaned_data['information']
                )
            else:
                comment.information = form.cleaned_data['information']
                comment.is_edited = True
                comment.save()
        else:
            show_form_errors(request, form)

    return HttpResponseRedirect(safe_redirect_url(request))


@login_required()
def comment_modal_delete_form_view(
    request: WSGIRequest,
    comment_pk: int,
    obj_pk: int,
    app_label: str,
    model_name: str
) -> HttpResponseRedirect | TemplateResponse:
    has_app_permission_or_404(request.user, app_label, model_name, 'change')

    comment = get_object_or_404(models.Comment, pk=comment_pk)
    obj = model_object_from_app_label(app_label, model_name, obj_pk)
    return_url = safe_redirect_url(request)

    if comment.user != request.user:
        messages.warning(request, 'You can only delete your comments.')
        return HttpResponseRedirect(return_url)

    form_action = reverse('django_spire:comment:delete_form', kwargs={
        'comment_pk': comment_pk,
        'obj_pk': obj_pk,
        'app_label': app_label,
        'model_name': model_name
    })

    def add_activity() -> None:
        obj.add_activity(
            user=request.user,
            verb='deleted',
            information=f'{request.user.get_full_name()} deleted a comment on "{obj}".',
        )

    return dispatch_modal_delete_form_content(
        request,
        obj=comment,
        form_action=form_action,
        activity_func=add_activity,
        return_url=return_url,
        show_success_message=True
    )
