from __future__ import annotations

from django.contrib.contenttypes.models import ContentType

from django_spire.comment.forms import CommentForm
from django_spire.core.tests.test_cases import BaseTestCase


class TestCommentForm(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.content_type = ContentType.objects.get_for_model(self.super_user)

    def test_valid_form(self) -> None:
        form = CommentForm(data={'information': 'Test comment'})
        assert form.is_valid() is True

    def test_form_save(self) -> None:
        form = CommentForm(data={'information': 'New comment'})
        assert form.is_valid() is True
        comment = form.save(commit=False)
        comment.content_type = self.content_type
        comment.object_id = self.super_user.pk
        comment.user = self.super_user
        comment.save()
        assert comment.information == 'New comment'
