from django.urls import path, include

app_name = 'task'

urlpatterns = [
    path('page/', include('test_project.app.task.urls.page_urls', namespace='page')),
    path('form/', include('test_project.app.task.urls.form_urls', namespace='form')),
    path('modal/', include('test_project.app.task.urls.modal_urls', namespace='modal')),
]
