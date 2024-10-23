from django.urls import include, path
from django_spire.landing import views

app_name = 'landing'

urlpatterns = [
    path('',
         views.home_view,
         name='home'),
]

# Contact Us #
# urlpatterns += [
#     path('contact-us/',
#          views.contact_us_view,
#          name='contact_us'),
#
#     path('contact-us/success/',
#          views.contact_us_success_view,
#          name='contact_form_success'),
# ]

# Boneyard #
urlpatterns += [
    path('boneyard/',
         views.boneyard_view,
         name='boneyard')
]

# Crypt #
urlpatterns += [
    path('crypt/',
         views.crypt_view,
         name='crypt')
]

# Asylum #
urlpatterns += [
    path('asylum/',
         views.asylum_view,
         name='asylum')
]

# Wasteland #
urlpatterns += [
    path('wasteland/',
         views.wasteland_view,
         name='wasteland')
]

urlpatterns += [
    path('component/',
        include('app.landing.component.urls', namespace='component')
    ),
]
