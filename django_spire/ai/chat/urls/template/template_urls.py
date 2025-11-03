from django.urls import path

from django_spire.ai.chat.views.template import template_views


app_name = 'template'

urlpatterns = [
    path("<int:pk>/confirm_delete", template_views.confirm_delete_view, name="confirm_delete"),
    path("load/", template_views.dialog_widget_view, name="load"),
    path("recent/", template_views.recent_chats_widget_view, name="recent"),
    path("search/", template_views.search_chats_results_widget_view, name="search"),
]
