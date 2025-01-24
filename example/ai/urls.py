from django.urls import path

from example.ai import views


app_name = 'ai'

urlpatterns = [
    path('home/', views.ai_home_view, name='home'),
]
