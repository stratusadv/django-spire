from __future__ import annotations

import datetime
import random

from django.utils.timezone import localdate, now

from example.models import TestModel


def generate_test_model() -> TestModel:
    return TestModel.objects.create(
        first_name='John',
        last_name='Doe',
        description='This is a sample description used for testing.',
        personality_type=random.choice(['int', 'ext']),
        email='johndoe@example.com',
        favorite_number=random.randint(0, 999),
        anniversary_datetime=now(),
        birth_date=localdate(),
        weight_lbs=round(random.uniform(100, 250), 3),
        best_friend=None,
        bed_time=datetime.time(hour=22, minute=0),
        likes_to_party=random.choice([True, False])
    )
