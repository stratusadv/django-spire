from __future__ import annotations

import uuid

from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from django.db import models
from django.test import TestCase

from django_spire.contrib.sync.django.serializer import SyncFieldSerializer


class SerializerTestModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    is_active = models.BooleanField(default=True)
    count = models.IntegerField(default=0)
    big_count = models.BigIntegerField(default=0)
    small_count = models.SmallIntegerField(default=0)
    positive_count = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0.0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    name = models.CharField(max_length=255, default='')
    notes = models.TextField(default='')
    created_date = models.DateField(null=True)
    created_datetime = models.DateTimeField(null=True)
    created_time = models.TimeField(null=True)
    duration = models.DurationField(null=True)
    metadata = models.JSONField(default=dict)
    parent = models.ForeignKey('self', null=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'sync_tests'
        managed = False


class SyncFieldSerializerSerializeTestCase(TestCase):
    def setUp(self) -> None:
        self.serializer = SyncFieldSerializer(SerializerTestModel)

    def test_serialize_bool_true(self) -> None:
        instance = SerializerTestModel(is_active=True)
        data = self.serializer.serialize(instance)
        assert data['is_active'] is True

    def test_serialize_bool_false(self) -> None:
        instance = SerializerTestModel(is_active=False)
        data = self.serializer.serialize(instance)
        assert data['is_active'] is False

    def test_serialize_bool_from_int(self) -> None:
        instance = SerializerTestModel(is_active=1)
        data = self.serializer.serialize(instance)
        assert data['is_active'] is True

    def test_serialize_uuid(self) -> None:
        pk = uuid.uuid4()
        instance = SerializerTestModel(id=pk)
        data = self.serializer.serialize(instance)
        assert data['id'] == str(pk)

    def test_serialize_integer(self) -> None:
        instance = SerializerTestModel(count=42)
        data = self.serializer.serialize(instance)
        assert data['count'] == 42

    def test_serialize_big_integer(self) -> None:
        instance = SerializerTestModel(big_count=9999999999)
        data = self.serializer.serialize(instance)
        assert data['big_count'] == 9999999999

    def test_serialize_small_integer(self) -> None:
        instance = SerializerTestModel(small_count=7)
        data = self.serializer.serialize(instance)
        assert data['small_count'] == 7

    def test_serialize_positive_integer(self) -> None:
        instance = SerializerTestModel(positive_count=10)
        data = self.serializer.serialize(instance)
        assert data['positive_count'] == 10

    def test_serialize_float(self) -> None:
        instance = SerializerTestModel(rating=3.14)
        data = self.serializer.serialize(instance)
        assert data['rating'] == 3.14

    def test_serialize_decimal(self) -> None:
        instance = SerializerTestModel(price=Decimal('19.99'))
        data = self.serializer.serialize(instance)
        assert data['price'] == '19.99'

    def test_serialize_char(self) -> None:
        instance = SerializerTestModel(name='test')
        data = self.serializer.serialize(instance)
        assert data['name'] == 'test'

    def test_serialize_text(self) -> None:
        instance = SerializerTestModel(notes='long text')
        data = self.serializer.serialize(instance)
        assert data['notes'] == 'long text'

    def test_serialize_date(self) -> None:
        d = date(2026, 4, 27)
        instance = SerializerTestModel(created_date=d)
        data = self.serializer.serialize(instance)
        assert data['created_date'] == '2026-04-27'

    def test_serialize_datetime(self) -> None:
        dt = datetime(2026, 4, 27, 12, 30, 0, tzinfo=timezone.utc)
        instance = SerializerTestModel(created_datetime=dt)
        data = self.serializer.serialize(instance)
        assert data['created_datetime'] == '2026-04-27T12:30:00+00:00'

    def test_serialize_time(self) -> None:
        t = time(14, 30, 0)
        instance = SerializerTestModel(created_time=t)
        data = self.serializer.serialize(instance)
        assert data['created_time'] == '14:30:00'

    def test_serialize_duration(self) -> None:
        td = timedelta(hours=2, minutes=30)
        instance = SerializerTestModel(duration=td)
        data = self.serializer.serialize(instance)
        assert data['duration'] == 9000.0

    def test_serialize_json_field(self) -> None:
        instance = SerializerTestModel(metadata={'key': 'value'})
        data = self.serializer.serialize(instance)
        assert data['metadata'] == {'key': 'value'}

    def test_serialize_foreign_key(self) -> None:
        parent_pk = uuid.uuid4()
        instance = SerializerTestModel(parent_id=parent_pk)
        data = self.serializer.serialize(instance)
        assert data['parent_id'] == str(parent_pk)

    def test_serialize_null_foreign_key(self) -> None:
        instance = SerializerTestModel(parent_id=None)
        data = self.serializer.serialize(instance)
        assert data['parent_id'] is None

    def test_serialize_null_datetime(self) -> None:
        instance = SerializerTestModel(created_datetime=None)
        data = self.serializer.serialize(instance)
        assert data['created_datetime'] is None

    def test_serialize_null_decimal(self) -> None:
        instance = SerializerTestModel(price=None)
        data = self.serializer.serialize(instance)
        assert data['price'] is None


class SyncFieldSerializerDeserializeTestCase(TestCase):
    def setUp(self) -> None:
        self.serializer = SyncFieldSerializer(SerializerTestModel)

    def test_deserialize_bool_true(self) -> None:
        data = self.serializer.deserialize({'is_active': True})
        assert data['is_active'] is True

    def test_deserialize_bool_false(self) -> None:
        data = self.serializer.deserialize({'is_active': False})
        assert data['is_active'] is False

    def test_deserialize_bool_from_int_zero(self) -> None:
        data = self.serializer.deserialize({'is_active': 0})
        assert data['is_active'] is False

    def test_deserialize_bool_from_int_one(self) -> None:
        data = self.serializer.deserialize({'is_active': 1})
        assert data['is_active'] is True

    def test_deserialize_uuid_string(self) -> None:
        pk = str(uuid.uuid4())
        data = self.serializer.deserialize({'id': pk})
        assert data['id'] == pk

    def test_deserialize_uuid_object(self) -> None:
        pk = uuid.uuid4()
        data = self.serializer.deserialize({'id': pk})
        assert data['id'] == str(pk)

    def test_deserialize_integer(self) -> None:
        data = self.serializer.deserialize({'count': 42})
        assert data['count'] == 42

    def test_deserialize_integer_from_string(self) -> None:
        data = self.serializer.deserialize({'count': '42'})
        assert data['count'] == 42

    def test_deserialize_float(self) -> None:
        data = self.serializer.deserialize({'rating': 3.14})
        assert data['rating'] == 3.14

    def test_deserialize_float_from_string(self) -> None:
        data = self.serializer.deserialize({'rating': '3.14'})
        assert data['rating'] == 3.14

    def test_deserialize_decimal_from_string(self) -> None:
        data = self.serializer.deserialize({'price': '19.99'})
        assert data['price'] == Decimal('19.99')

    def test_deserialize_decimal_from_int(self) -> None:
        data = self.serializer.deserialize({'price': 20})
        assert data['price'] == Decimal('20')

    def test_deserialize_decimal_from_decimal(self) -> None:
        data = self.serializer.deserialize({'price': Decimal('19.99')})
        assert data['price'] == Decimal('19.99')

    def test_deserialize_date_from_string(self) -> None:
        data = self.serializer.deserialize({'created_date': '2026-04-27'})
        assert data['created_date'] == date(2026, 4, 27)

    def test_deserialize_date_from_date(self) -> None:
        d = date(2026, 4, 27)
        data = self.serializer.deserialize({'created_date': d})
        assert data['created_date'] == d

    def test_deserialize_datetime_from_string(self) -> None:
        data = self.serializer.deserialize({'created_datetime': '2026-04-27T12:30:00+00:00'})
        assert data['created_datetime'] == datetime(2026, 4, 27, 12, 30, 0, tzinfo=timezone.utc)

    def test_deserialize_datetime_from_datetime(self) -> None:
        dt = datetime(2026, 4, 27, 12, 30, 0, tzinfo=timezone.utc)
        data = self.serializer.deserialize({'created_datetime': dt})
        assert data['created_datetime'] == dt

    def test_deserialize_time_from_string(self) -> None:
        data = self.serializer.deserialize({'created_time': '14:30:00'})
        assert data['created_time'] == time(14, 30, 0)

    def test_deserialize_time_from_time(self) -> None:
        t = time(14, 30, 0)
        data = self.serializer.deserialize({'created_time': t})
        assert data['created_time'] == t

    def test_deserialize_duration_from_seconds(self) -> None:
        data = self.serializer.deserialize({'duration': 9000.0})
        assert data['duration'] == timedelta(hours=2, minutes=30)

    def test_deserialize_duration_from_int(self) -> None:
        data = self.serializer.deserialize({'duration': 3600})
        assert data['duration'] == timedelta(hours=1)

    def test_deserialize_duration_from_timedelta(self) -> None:
        td = timedelta(minutes=45)
        data = self.serializer.deserialize({'duration': td})
        assert data['duration'] == td

    def test_deserialize_json_passthrough(self) -> None:
        data = self.serializer.deserialize({'metadata': {'key': 'value'}})
        assert data['metadata'] == {'key': 'value'}

    def test_deserialize_char_passthrough(self) -> None:
        data = self.serializer.deserialize({'name': 'test'})
        assert data['name'] == 'test'

    def test_deserialize_null_preserved(self) -> None:
        data = self.serializer.deserialize({'created_datetime': None})
        assert data['created_datetime'] is None

    def test_deserialize_foreign_key_string(self) -> None:
        pk = str(uuid.uuid4())
        data = self.serializer.deserialize({'parent_id': pk})
        assert data['parent_id'] == pk

    def test_deserialize_foreign_key_null(self) -> None:
        data = self.serializer.deserialize({'parent_id': None})
        assert data['parent_id'] is None

    def test_deserialize_unknown_key_passthrough(self) -> None:
        data = self.serializer.deserialize({'unknown_field': 'value'})
        assert data['unknown_field'] == 'value'


class SyncFieldSerializerRoundTripTestCase(TestCase):
    def setUp(self) -> None:
        self.serializer = SyncFieldSerializer(SerializerTestModel)

    def test_round_trip_all_types(self) -> None:
        pk = uuid.uuid4()
        parent_pk = uuid.uuid4()
        dt = datetime(2026, 4, 27, 12, 30, 0, tzinfo=timezone.utc)
        d = date(2026, 4, 27)
        t = time(14, 30, 0)
        td = timedelta(hours=2, minutes=30)

        instance = SerializerTestModel(
            id=pk,
            is_active=True,
            count=42,
            big_count=9999999999,
            small_count=7,
            positive_count=10,
            rating=3.14,
            price=Decimal('19.99'),
            name='test',
            notes='long text',
            created_date=d,
            created_datetime=dt,
            created_time=t,
            duration=td,
            metadata={'key': 'value'},
            parent_id=parent_pk,
        )

        serialized = self.serializer.serialize(instance)
        deserialized = self.serializer.deserialize(serialized)

        assert deserialized['id'] == str(pk)
        assert deserialized['is_active'] is True
        assert deserialized['count'] == 42
        assert deserialized['big_count'] == 9999999999
        assert deserialized['small_count'] == 7
        assert deserialized['positive_count'] == 10
        assert deserialized['rating'] == 3.14
        assert deserialized['price'] == Decimal('19.99')
        assert deserialized['name'] == 'test'
        assert deserialized['notes'] == 'long text'
        assert deserialized['created_date'] == d
        assert deserialized['created_datetime'] == dt
        assert deserialized['created_time'] == t
        assert deserialized['duration'] == td
        assert deserialized['metadata'] == {'key': 'value'}
        assert deserialized['parent_id'] == str(parent_pk)

    def test_round_trip_all_nulls(self) -> None:
        instance = SerializerTestModel(
            created_date=None,
            created_datetime=None,
            created_time=None,
            duration=None,
            parent_id=None,
        )

        serialized = self.serializer.serialize(instance)
        deserialized = self.serializer.deserialize(serialized)

        assert deserialized['created_date'] is None
        assert deserialized['created_datetime'] is None
        assert deserialized['created_time'] is None
        assert deserialized['duration'] is None
        assert deserialized['parent_id'] is None
