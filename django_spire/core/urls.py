from django.contrib import admin
from django.urls import path, include

app_name = 'core'
urlpatterns = [
    path('comment/', include('app.core.comment.urls', namespace='comment')),
]
