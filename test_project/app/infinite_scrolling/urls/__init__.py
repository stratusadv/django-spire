from django.urls.conf import include, path


app_name = 'infinite_scrolling'

urlpatterns = [
    path('form/', include('test_project.apps.infinite_scrolling.urls.form_urls', namespace='form')),
    path('page/', include('test_project.apps.infinite_scrolling.urls.page_urls', namespace='page')),
    path('template/', include('test_project.apps.infinite_scrolling.urls.template_urls', namespace='template')),
]
