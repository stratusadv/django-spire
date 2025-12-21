from __future__ import annotations

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from django_spire.history.viewed.models import Viewed


class TestViewed(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'  # noqa: S106
        )
        self.content_type = ContentType.objects.get_for_model(User)

    def test_create_viewed(self) -> None:
        viewed = Viewed.objects.create(
            content_type=self.content_type,
            object_id=self.user.pk,
            user=self.user
        )

        assert viewed.pk is not None
        assert viewed.user == self.user
        assert viewed.content_object == self.user

    def test_created_datetime_auto_set(self) -> None:
        viewed = Viewed.objects.create(
            content_type=self.content_type,
            object_id=self.user.pk,
            user=self.user
        )

        assert viewed.created_datetime is not None

    def test_str_representation(self) -> None:
        viewed = Viewed.objects.create(
            content_type=self.content_type,
            object_id=self.user.pk,
            user=self.user
        )

        assert 'testuser' in str(viewed)
        assert 'viewed' in str(viewed)
