from django_spire.help_desk.views import form_views

app_name = 'form'

urlpatterns = [
    ('create/', form_views.ticket_create_form_view, 'create'),
    ('<int:pk>/update/', form_views.ticket_update_form_view, 'update'),
    ('<int:pk>/delete/', form_views.ticket_delete_form_view, 'delete'),
]

