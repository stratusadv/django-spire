from django.urls import path, include

from test_project.apps.comment import views


app_name = 'comment'

urlpatterns = [
    path('page/', include('test_project.apps.comment.urls.page_urls', namespace='page')),
]
