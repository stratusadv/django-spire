from django.urls import path, include


app_name = 'comment'

urlpatterns = [path('page/', include('test_project.app.comment.urls.page_urls', namespace='page'))]
