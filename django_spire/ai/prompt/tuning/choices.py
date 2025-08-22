from django.db.models import IntegerChoices


class OutcomeRatingChoices(IntegerChoices):
    TERRIBLE = 1, 'terrible'
    BAD = 2, 'bad'
    OK = 3, 'ok'
    GOOD = 4, 'good'
    GREAT = 5, 'great'
    AMAZING = 6, 'amazing'
