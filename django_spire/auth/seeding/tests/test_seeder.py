from typing import Any

from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.test import TestCase
from unittest.mock import patch

from dandy.llm.service import LlmService

from django_spire.auth.seeding.seeder import UserSeeder


class _FakeFieldIntel:
    def __init__(self, values: dict[str, Any]) -> None:
        self._values = values

    def model_dump(self) -> dict[str, Any]:
        return self._values


class UserSeederTestCase(TestCase):
    def _llm_patch(self) -> Any:
        fake_intel = _FakeFieldIntel({'email': 'constant@example.com'})
        return patch.object(LlmService, 'prompt_to_intel', return_value=fake_intel)

    def _seed_users(self, count: int) -> QuerySet:
        with self._llm_patch():
            return UserSeeder(count=count, verbose=False).seed_database()

    def test_usernames_are_unique_across_batch(self):
        self._seed_users(3)

        usernames = list(User.objects.values_list('username', flat=True))

        assert len(usernames) == 3
        assert len(set(usernames)) == 3

    def test_username_matches_seeded_email(self):
        self._seed_users(1)

        user = User.objects.get()

        assert user.email == 'constant@example.com'
        assert user.username == 'constant@example.com'

    def test_duplicate_emails_get_suffixed_usernames(self):
        self._seed_users(3)

        users = list(User.objects.values_list('email', 'username'))

        assert all(email == 'constant@example.com' for email, _ in users)
        assert {username for _, username in users} == {
            'constant@example.com',
            'constant@example.com-2',
            'constant@example.com-3',
        }

    def test_usernames_are_unique_against_existing_rows(self):
        User.objects.create(username='constant@example.com', email='constant@example.com')
        self._seed_users(3)

        usernames = set(User.objects.values_list('username', flat=True))

        assert usernames == {
            'constant@example.com',
            'constant@example.com-2',
            'constant@example.com-3',
            'constant@example.com-4',
        }

    def test_reseed_database_stays_unique_against_first_batch(self):
        seeder = UserSeeder(count=3, verbose=False)

        with self._llm_patch():
            seeder.seed_database()
            seeder.reseed_database()

        usernames = list(User.objects.values_list('username', flat=True))

        assert len(usernames) == 6
        assert len(set(usernames)) == 6
