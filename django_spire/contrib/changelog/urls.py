from django.urls import path

from django_spire.contrib.changelog import views

app_name = 'changelog'

urlpatterns = [
    path('content/', views.changelog_card_content_view, name='content'),
]