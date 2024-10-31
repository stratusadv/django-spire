from django.urls import include, path


app_name = 'comments'

urlpatterns = [
    path('comment/',
        include('django_spire.comment.urls',
        namespace='comment')
    ),
]
