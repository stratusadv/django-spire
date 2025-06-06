from django_spire.help_desk.views import page_views

app_name = 'page'


urlpatterns=[
    ('list/', page_views.ticket_list_view, 'list'),
    ('<int:pk>/detail/', page_views.ticket_detail_view, 'detail'),
]