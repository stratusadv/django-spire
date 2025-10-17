from django.urls import include, path


app_name = 'form'

urlpatterns = [
    path('editable/', include('django_spire.form.editable.urls', namespace='editable')),
]
