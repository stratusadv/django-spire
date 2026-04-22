from django.urls import path, include

from test_project.app.ai import views


app_name = 'ai'

urlpatterns = [
    path('home/', views.ai_home_view, name='home'),
]
