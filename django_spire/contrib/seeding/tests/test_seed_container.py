import pytest
from django.test import TestCase

from django_spire.contrib.seeding.exceptions import DjangoSpireSeederError
from django_spire.contrib.seeding.seed.seed import Seed


class TestSeedContainer(TestCase):
    def test_getitem_returns_value(self):
        seed = Seed({'name': 'Test Name', 'value': 42})
        assert seed['name'] == 'Test Name'
        assert seed['value'] == 42

    def test_getitem_missing_key_raises(self):
        seed = Seed({'name': 'Test Name'})
        with pytest.raises(KeyError):
            _ = seed['missing']

    def test_setitem_sets_value(self):
        seed = Seed({'name': 'Original'})
        seed['name'] = 'Updated'
        assert seed['name'] == 'Updated'

    def test_setitem_new_key(self):
        seed = Seed({'name': 'Original'})
        seed['status'] = 'active'
        assert seed['status'] == 'active'

    def test_delitem_removes_key(self):
        seed = Seed({'name': 'Test', 'value': 42})
        del seed['value']
        with pytest.raises(KeyError):
            _ = seed['value']

    def test_to_dict_returns_underlying_dict(self):
        data = {'name': 'Test', 'status': 'active', 'count': 5}
        seed = Seed(data)
        assert seed.to_dict() == data
        assert seed.to_dict() is not data

    def test_repr_returns_dict_repr(self):
        data = {'name': 'Test'}
        seed = Seed(data)
        assert repr(seed) == repr(data)

    def test_equality_same_data(self):
        seed1 = Seed({'name': 'Test', 'status': 'active'})
        seed2 = Seed({'name': 'Test', 'status': 'active'})
        assert seed1 == seed2

    def test_inequality_different_data(self):
        seed1 = Seed({'name': 'Test A'})
        seed2 = Seed({'name': 'Test B'})
        assert seed1 != seed2

    def test_nested_dict_access(self):
        seed = Seed({'user': {'name': 'John', 'age': 30}})
        assert seed['user']['name'] == 'John'

    def test_list_value(self):
        seed = Seed({'items': [1, 2, 3]})
        assert seed['items'] == [1, 2, 3]

    def test_none_value(self):
        seed = Seed({'value': None})
        assert seed['value'] is None

    def test_boolean_values(self):
        seed = Seed({'active': True, 'deleted': False})
        assert seed['active'] is True
        assert seed['deleted'] is False


class TestDjangoSpireSeederError(TestCase):
    def test_inherits_from_django_spire_error(self):
        from django_spire.exceptions import DjangoSpireError
        assert issubclass(DjangoSpireSeederError, DjangoSpireError)

    def test_can_be_raised_with_message(self):
        with pytest.raises(DjangoSpireSeederError, match='Test error message'):
            raise DjangoSpireSeederError('Test error message')

    def test_can_be_raised_without_message(self):
        with pytest.raises(DjangoSpireSeederError):
            raise DjangoSpireSeederError()

    def test_can_catch_as_parent_exception(self):
        with pytest.raises(Exception, match='Field name error'):
            raise DjangoSpireSeederError('Field name error')

    def test_equality_of_messages(self):
        error1 = DjangoSpireSeederError('Same message')
        error2 = DjangoSpireSeederError('Same message')
        assert str(error1) == str(error2)

    def test_message_formatting(self):
        error = DjangoSpireSeederError('Invalid field name(s): fake_field')
        assert 'fake_field' in str(error)