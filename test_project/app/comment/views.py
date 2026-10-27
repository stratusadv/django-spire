from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.comment.navigation import CommentNavigation
from django_spire.contrib.redirects import safe_redirect_url
from django_spire.contrib.shortcuts import get_object_or_null_obj
from test_project.app.comment import forms, models

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import HttpResponseRedirect


def comment_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    comment = get_object_or_404(models.CommentExample, pk=pk)

    nav = CommentNavigation()
    nav.breadcrumbs.add(str(comment), None)
    nav.page_title = str(comment)
    context = nav.as_context()
    context['comment_example'] = comment
    context['page_description'] = 'Detail View'

    return TemplateResponse(
        request, context=context, template='comment/page/comment_detail_page.html'
    )


def comment_form_view(request: WSGIRequest, pk: int) -> HttpResponseRedirect | TemplateResponse:
    comment = get_object_or_null_obj(models.CommentExample, pk=pk)
    return_url = safe_redirect_url(request, fallback=reverse('comment:page:list'))
    form = forms.CommentExampleForm(request.POST or None, instance=comment)

    if form.is_valid():
        form.save()
        return redirect(return_url)

    nav = CommentNavigation()
    nav.breadcrumbs.add(str(comment) if comment.pk else 'New Comment', None)
    nav.page_title = str(comment) if comment.pk else 'New Comment'
    context = nav.as_context()
    context['form'] = form
    context['page_description'] = 'Edit' if comment.pk else 'Create'
    context['return_url'] = return_url

    return TemplateResponse(
        request, context=context, template='comment/page/comment_form_page.html'
    )
