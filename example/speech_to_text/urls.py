from django.urls import path

from example.speech_to_text import views


app_name = 'speech_to_text'

urlpatterns = [
    path('home/', views.speech_to_text_home_view, name='home'),
]
