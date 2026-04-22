from django.urls.conf import include, path


app_name = 'lazy_tabs'

urlpatterns = [
    path('page/', include('test_project.apps.lazy_tabs.urls.page_urls', namespace='page')),
    path('template/', include('test_project.apps.lazy_tabs.urls.template_urls', namespace='template')),
]
