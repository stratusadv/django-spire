from django.urls import include, path

app_name = 'metrics'

urlpatterns = [path('page/', include('test_project.app.metrics.urls.page_urls', namespace='page'))]
