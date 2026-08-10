import enum

from django.db.models import TextChoices
from django.test import TestCase

from django_spire.auth.user.models import AuthUser
from django_spire.contrib.seeding import Seeder
from django_spire.contrib.seeding.field.seed.model_seed import OrderedForeignKeyModelFieldSeed
from django_spire.contrib.seeding.field.seed.ordered_seed import OrderedSequenceFieldSeed
from django_spire.contrib.seeding.field.seed.random_seed import RandomEnumFieldSeed


class TestModelFieldSeedHelper(TestCase):
    def test_random_field_choice_returns_random_field_seed(self):
        class Status(enum.Enum):
            PENDING = 'pending'
            ACTIVE = 'active'
            COMPLETED = 'completed'

        seed = Seeder.model.random_field_choice(Status)
        assert isinstance(seed, RandomEnumFieldSeed)
        assert seed.enum_ is Status

    def test_random_field_choice_generates_enum_value(self):
        class Status(enum.Enum):
            A = 'a'
            B = 'b'

        seed = Seeder.model.random_field_choice(Status)
        value = seed.generate_value(0)
        assert value in list(Status)

    def test_random_field_choice_with_django_choices(self):
        class Status(TextChoices):
            PENDING = 'pending', 'Pending'
            ACTIVE = 'active', 'Active'
            COMPLETED = 'completed', 'Completed'

        seed = Seeder.model.random_field_choice(Status)
        assert isinstance(seed, RandomEnumFieldSeed)
        value = seed.generate_value(0)
        assert value in list(Status)

    def test_ordered_field_choice_returns_ordered_sequence_field_seed(self):
        class Status(enum.Enum):
            PENDING = 'pending'
            ACTIVE = 'active'
            COMPLETED = 'completed'

        seed = Seeder.model.ordered_field_choice(Status)
        assert isinstance(seed, OrderedSequenceFieldSeed)
        assert seed.sequence == list(Status)
        assert seed.wrap is False

    def test_ordered_field_choice_generates_values_in_order(self):
        class Status(enum.Enum):
            A = 'a'
            B = 'b'

        seed = Seeder.model.ordered_field_choice(Status)
        assert seed.generate_value(0) == Status.A
        assert seed.generate_value(1) == Status.B

    def test_ordered_field_choice_with_wrap_cycles(self):
        class Status(enum.Enum):
            A = 'a'
            B = 'b'

        seed = Seeder.model.ordered_field_choice(Status, wrap=True)
        assert seed.generate_value(0) == Status.A
        assert seed.generate_value(1) == Status.B
        assert seed.generate_value(2) == Status.A

    def test_ordered_field_choice_with_django_choices(self):
        class Status(TextChoices):
            PENDING = 'pending', 'Pending'
            ACTIVE = 'active', 'Active'
            COMPLETED = 'completed', 'Completed'

        seed = Seeder.model.ordered_field_choice(Status)
        assert seed.sequence == list(Status)

    def test_ordered_foreign_key_default_wrap_false(self):
        seed = Seeder.model.ordered_foreign_key(AuthUser)
        assert isinstance(seed, OrderedForeignKeyModelFieldSeed)
        assert seed.wrap is False

    def test_ordered_foreign_key_with_wrap(self):
        seed = Seeder.model.ordered_foreign_key(AuthUser, wrap=True)
        assert isinstance(seed, OrderedForeignKeyModelFieldSeed)
        assert seed.wrap is True

    def test_ordered_queryset_foreign_key_default_wrap_false(self):
        seed = Seeder.model.ordered_queryset_foreign_key(AuthUser.objects.all())
        assert isinstance(seed, OrderedForeignKeyModelFieldSeed)
        assert seed.wrap is False

    def test_ordered_queryset_foreign_key_with_wrap(self):
        seed = Seeder.model.ordered_queryset_foreign_key(AuthUser.objects.all(), wrap=True)
        assert isinstance(seed, OrderedForeignKeyModelFieldSeed)
        assert seed.wrap is True
