from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.comment import models
from django_spire.comment.forms import CommentForm
from django_spire.forms import show_form_errors
from django_spire.core.redirect import safe_redirect_url
from django_spire.shortcuts import get_object_or_null_obj, model_object_from_app_label
from django_spire.permission.utils import has_app_permission_or_404
from django_spire.views.modal_views import dispatch_modal_delete_form_content

from django_glue.glue import glue_model


@login_required()
def comment_modal_form_content(request, comment_pk: int, obj_pk: int, app_label: str, model_name: str):
    has_app_permission_or_404(request.user, app_label, model_name, 'change')

    if comment_pk == 0:
        comment = get_object_or_null_obj(models.Comment, pk=comment_pk)
    else:
        comment = get_object_or_404(models.Comment, pk=comment_pk, user__id=request.user.pk)

    glue_model(request, 'comment', comment)

    context_data = {
        'app_label': app_label,
        'model_name': model_name,
        'comment': comment,
        'obj_pk': obj_pk,
    }

    return TemplateResponse(
        request,
        context=context_data,
        template='spire/comment/form/comment_form.html',
    )


@login_required()
def comment_form_view(request, comment_pk: int, obj_pk: int, app_label: str, model_name: str):
    has_app_permission_or_404(request.user, app_label, model_name, 'change')

    if comment_pk == 0:
        comment = get_object_or_null_obj(models.Comment, pk=comment_pk)
    else:
        comment = get_object_or_404(models.Comment, pk=comment_pk, user__id=request.user.pk)

    obj = model_object_from_app_label(app_label, model_name, obj_pk)

    if not hasattr(obj, 'add_comment'):
        raise Exception(f'Object {obj} does not have the comment model mixin.')

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            # Todo: Create comment factory.
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
def comment_modal_delete_form_view(request, comment_pk: int, obj_pk: int, app_label: str, model_name: str):
    has_app_permission_or_404(request.user, app_label, model_name, 'change')

    comment = get_object_or_404(models.Comment, pk=comment_pk)
    obj = model_object_from_app_label(app_label, model_name, obj_pk)
    return_url = safe_redirect_url(request)

    if comment.user != request.user:
        messages.warning(request, 'You can only delete your comments.')
        return HttpResponseRedirect(return_url)

    form_action = reverse('core:comment:delete_form', kwargs={
        'comment_pk': comment_pk,
        'obj_pk': obj_pk,
        'app_label': app_label,
        'model_name': model_name
    })

    def add_activity():
        obj.add_activity(
            user=request.user,
            verb='deleted',
            device=request.device,
            information=f'{request.user.get_full_name()} deleted a comment on "{obj}".'
        )

    return dispatch_modal_delete_form_content(
        request,
        obj=comment,
        form_action=form_action,
        activity_func=add_activity,
        return_url=return_url,
    )
