from django_spire.core.tests.test_cases import BaseTestCase

from django_spire.user_account.tests.factories import create_super_user
from django_spire.history.tests.factories import create_test_cookbook


class ActivityLogMixinTest(BaseTestCase):
    def setUp(self):
        self.test_user = create_super_user()
        self.test_recipient = create_super_user()
        self.test_subscribers = [create_super_user() for _ in range(3)]
        self.test_cookbook = create_test_cookbook()

    # TODO: Fix tests
    # def test_add_activity_no_subscribers(self):
    #     activity = self.test_cookbook.add_activity(
    #         self.test_user,
    #         'Create',
    #         'The rat created a cookbook',
    #         self.test_recipient,
    #     )
    #
    #     # Asserts
    #     self.assertTrue(True)
    #
    # def test_add_activity_with_subscribers(self):
    #     activity = self.test_cookbook.add_activity(
    #         self.test_user,
    #         'Create',
    #         'The rat created a cookbook',
    #         self.test_recipient,
    #         self.test_subscribers,
    #     )
    #
    #     # Asserts
    #     self.assertTrue(True)
