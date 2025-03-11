from django.urls import path, include


urlpatterns = [
    path('dummy/', include('testing.dummy.urls')),
]
