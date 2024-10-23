from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.user_account.profile.models import UserProfile
from django_spire.user_account.tests.factories import create_user


class UserProfileTestCase(BaseTestCase):
    def setUp(self):
        self.user = create_user(username="Wesley", password="goat_99")

    def test_user_profile_receiver(self):
        profile = self.user.profile
        self.assertTrue(UserProfile.objects.filter(user=profile.user_id).exists())
