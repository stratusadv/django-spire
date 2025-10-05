from django.urls import path

from test_project.apps.ai.chat import views


app_name = 'chat'

urlpatterns = [
    path('home/', views.chat_home_view, name='home'),
]
