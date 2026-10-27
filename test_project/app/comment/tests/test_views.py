from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from test_project.app.comment.models import CommentExample
from test_project.app.comment.tests.factories import create_test_comment_example


class CommentFormViewTestCase(BaseTestCase):
    def test_a_pk_of_zero_creates_a_comment_and_returns_to_the_list(self) -> None:
        form_url = reverse('comment:page:form', kwargs={'pk': 0})
        list_url = reverse('comment:page:list')

        response = self.client.post(
            f'{form_url}?return_url={list_url}',
            {'name': 'Fresh', 'description': 'New one'},
        )

        assert response.status_code == 302
        assert response.url == list_url
        assert CommentExample.objects.filter(name='Fresh', description='New one').exists()

    def test_an_existing_comment_is_edited(self) -> None:
        comment = create_test_comment_example(name='Old')

        response = self.client.post(
            reverse('comment:page:form', kwargs={'pk': comment.pk}),
            {'name': 'New', 'description': 'Edited'},
        )

        comment.refresh_from_db()

        assert response.status_code == 302
        assert comment.name == 'New'

    def test_the_form_page_carries_its_return_url_into_the_post(self) -> None:
        comment = create_test_comment_example()
        list_url = reverse('comment:page:list')

        response = self.client.get(
            reverse('comment:page:form', kwargs={'pk': comment.pk}),
            {'return_url': list_url},
        )

        assert response.status_code == 200
        assert f'action="?return_url={list_url}"' in response.content.decode()
