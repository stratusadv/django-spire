from django.urls import path, include

from test_project.app.comment import views


app_name = 'comment'

urlpatterns = [
    path('page/', include('test_project.app.comment.urls.page_urls', namespace='page')),
]
