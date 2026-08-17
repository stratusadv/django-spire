from __future__ import annotations

from typing import TYPE_CHECKING

from django_glue import Glue

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from django_spire.auth.group.utils import has_app_permission_or_404
from django_spire.comment import models
from django_spire.comment.forms import CommentForm
from django_spire.comment.navigation import CommentNavigation
from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm
from django_spire.contrib.form.tools import show_form_errors
from django_spire.contrib.redirects import safe_redirect_url
from django_spire.contrib.shortcuts import get_object_or_null_obj, model_object_from_app_label

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required()
def comment_modal_form_content(
    request: WSGIRequest, comment_pk: int, obj_pk: int, app_label: str, model_name: str
) -> TemplateResponse:
    has_app_permission_or_404(request.user, app_label, model_name, 'change')

    if comment_pk == 0:
        comment = get_object_or_null_obj(models.Comment, pk=comment_pk)
    else:
        comment = get_object_or_404(models.Comment, pk=comment_pk, user__id=request.user.pk)

    Glue.model(request, 'comment', comment)

    nav = CommentNavigation()
    nav.page_title = 'Add Comment'
    context = nav.as_context()
    context['app_label'] = app_label
    context['model_name'] = model_name
    context['comment'] = comment
    context['obj_pk'] = obj_pk
    return TemplateResponse(request, 'django_spire/comment/form/comment_form.html', context=context)


@login_required()
def comment_form_view(
    request: WSGIRequest, comment_pk: int, obj_pk: int, app_label: str, model_name: str
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
            if comment_pk == 0:
                obj.add_comment(user=request.user, information=form.cleaned_data['information'])
            else:
                comment.information = form.cleaned_data['information']
                comment.is_edited = True
                comment.save()
        else:
            show_form_errors(request, form)

    return HttpResponseRedirect(safe_redirect_url(request))


@login_required()
def comment_modal_delete_form_view(
    request: WSGIRequest, comment_pk: int, obj_pk: int, app_label: str, model_name: str
) -> HttpResponseRedirect | TemplateResponse:
    has_app_permission_or_404(request.user, app_label, model_name, 'change')

    comment = get_object_or_404(models.Comment, pk=comment_pk)
    return_url = safe_redirect_url(request)

    if comment.user != request.user:
        messages.warning(request, 'You can only delete your comments.')
        return HttpResponseRedirect(return_url)

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=comment)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                comment.set_deleted()

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=comment)

    context = {
        'form': form,
        'form_description': 'Are you sure you would like to delete this comment?',
        'form_title': 'Delete Comment',
    }

    return TemplateResponse(
        request,
        'django_spire/form/card/delete_confirmation_form_card.html',
        context=context,
    )
