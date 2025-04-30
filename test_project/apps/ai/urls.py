from django.urls import path, include

from test_project.apps.ai import views


app_name = 'ai'

urlpatterns = [
    path('home/', views.ai_home_view, name='home'),
    path('chat/', include('test_project.apps.ai.chat.urls', namespace='chat'), name='chat'),
]
