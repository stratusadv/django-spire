from django.urls import path, include

from example.ai import views


app_name = 'ai'

urlpatterns = [
    path('home/', views.ai_home_view, name='home'),
    path('chat/', include('example.ai.chat.urls', namespace='chat'), name='chat'),
]
