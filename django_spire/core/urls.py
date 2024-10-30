from django.urls import include, path


app_name = 'core'

urlpatterns = [
    path(
        'comment/',
        include('app.core.comment.urls', namespace='comment')
    ),
]
