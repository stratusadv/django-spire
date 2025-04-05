from django.urls import path

from example.speech_to_text import views


app_name = 'ai'

urlpatterns = [
    path('home/', views.ai_home_view, name='home'),
]
