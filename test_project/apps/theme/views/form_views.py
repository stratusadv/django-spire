# from __future__ import annotations
#
# from typing_extensions import TYPE_CHECKING
#
# from django.contrib.auth.decorators import permission_required
# from django.shortcuts import get_object_or_404, redirect
# from django.template.response import TemplateResponse
# from django.urls import reverse
#
# from django_spire.core.redirect.safe_redirect import safe_redirect_url
# from django_spire.core.shortcuts import get_object_or_null_obj
# from django_spire.contrib.form.utils import show_form_errors
# from django_spire.history.activity.utils import add_form_activity
# from django_spire.contrib.generic_views import portal_views, modal_views
#
# import django_glue as dg
#
# from test_project.apps.theme import forms, models
#
#
# if TYPE_CHECKING:
#     from django.core.handlers.wsgi import WSGIRequest
#
#
# @permission_required('apps.delete_appstheme')
# def apps_theme_delete_form_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
#     theme = get_object_or_404(models.Theme, pk=pk)
#
#     form_action = reverse(
#         'apps:theme:delete_form_modal',
#         kwargs={'pk': pk}
#     )
#
#     def add_activity() -> None:
#         theme.add_activity(
#             user=request.user,
#             verb='deleted',
#             device=request.device,
#             information=f'{request.user.get_full_name()} deleted a theme on "{theme.apps}".'
#         )
#
#     fallback = reverse(
#         'apps:detail',
#         kwargs={'pk': theme.apps.pk}
#     )
#
#     return_url = safe_redirect_url(request, fallback=fallback)
#
#     return modal_views.dispatch_modal_delete_form_content(
#         request,
#         obj=theme,
#         form_action=form_action,
#         activity_func=add_activity,
#         return_url=return_url,
#     )
#
#
# @permission_required('apps.delete_appstheme')
# def apps_theme_delete_view(request: WSGIRequest, pk: int) -> TemplateResponse:
#     theme = get_object_or_404(models.Theme, pk=pk)
#
#     return_url = request.GET.get(
#         'return_url',
#         reverse('theme:page:list')
#     )
#
#     return portal_views.delete_form_view(
#         request,
#         obj=theme,
#         return_url=return_url
#     )
#
#
# @permission_required('apps.change_appstheme')
# def apps_theme_form_content_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
#     theme = get_object_or_404(models.Theme, pk=pk)
#
#     dg.glue_model_object(request, 'theme', theme)
#
#     context_data = {
#         'theme': theme
#     }
#
#     return TemplateResponse(
#         request,
#         context=context_data,
#         template='theme/modal/content/theme_form_modal_content.html'
#     )
#
#
# @permission_required('apps.change_appstheme')
# def apps_theme_form_view(request: WSGIRequest, pk: int) -> TemplateResponse:
#     theme = get_object_or_null_obj(models.Theme, pk=pk)
#
#     dg.glue_model_object(request, 'theme', theme, 'view')
#
#     if request.method == 'POST':
#         form = forms.PlaceholderForm(request.POST, instance=theme)
#
#         if form.is_valid():
#             theme = form.save()
#             add_form_activity(theme, pk, request.user)
#
#             return redirect(
#                 request.GET.get(
#                     'return_url',
#                     reverse('theme:page:list')
#                 )
#             )
#
#         show_form_errors(request, form)
#     else:
#         form = forms.PlaceholderForm(instance=theme)
#
#     return portal_views.form_view(
#         request,
#         form=form,
#         obj=theme,
#         template='theme/page/theme_form_page.html'
#     )
