from django.urls import path

from examples.component import views


app_name = 'component'


urlpatterns = [
    path('', views.home_view, name='home'),

    path('accordion', views.accordion_view, name='accordion'),
    path('badge', views.badge_view, name='badge'),
    path('base', views.base_view, name='base'),
    path('button', views.button_view, name='button'),
    path('card', views.card_view, name='card'),
    path('comment', views.comment_view, name='comment'),
    path('container', views.container_view, name='container'),
    path('dropdown', views.dropdown_view, name='dropdown'),
    path('element', views.element_view, name='element'),
    path('file', views.file_view, name='file'),
    path('form', views.form_view, name='form'),
    path('help', views.help_view, name='help'),
    path('item', views.item_view, name='item'),
    path('modal', views.modal_view, name='modal'),
    path('modal_content', views.modal_content_view, name='modal_content'),
    path('navigation', views.navigation_view, name='navigation'),
    path('notification', views.notification_view, name='notification'),
    path('page', views.page_view, name='page'),
    path('tab', views.tab_view, name='tab')
]
