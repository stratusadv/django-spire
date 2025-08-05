from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.sms.tools import format_to_international_phone_number


class TestSMSTools(BaseTestCase):

    def test_local_to_international_phone_number(self):
        phone_numbers = (
            '622 415 2736',
            '881-553-4599 x702',
            '+1 (588) 841-1582',
            '+1 (205) 461-5871',
            '742-180-9582',
            '691 287 8913',
            '(461) 107-2210 x009',
            '836-958-3866 x265',
            '615.332.9689',
            '919-286-3636 x939',
            '368.447-9514',
            '4563219876'
        )
        expected_phone_numbers = (
            '+16224152736',
            '+18815534599',
            '+15888411582',
            '+12054615871',
            '+17421809582',
            '+16912878913',
            '+14611072210',
            '+18369583866',
            '+16153329689',
            '+19192863636',
            '+13684479514',
            '+14563219876'
        )
        formatted_phone_numbers = [format_to_international_phone_number(phone_number) for phone_number in phone_numbers]
        self.assertSequenceEqual(formatted_phone_numbers, expected_phone_numbers)

    def test_invalid_phone_number(self):
        phone_numbers = (
            'ABC-DEF-GHIJ',
            '123',
            '1',
            '12345678901234567890',
            '',
            '32145698765', # excess 1 digit
            '403000123', # missing 1 digit
            '36800012', # missing 2 digits
        )
        for phone_number in phone_numbers:
            self.assertRaises(
                ValueError,
                format_to_international_phone_number,
                phone_number
            )