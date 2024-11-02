from django.db import models


class RecipeCourseChoices(models.TextChoices):
    BREAKFAST = 'bre', 'Breakfast'
    APPETIZER = 'app', 'Appetizer'
    MAIN = 'mai', 'Main Course'
    DESSERT = 'des', 'Dessert'
    SOUP = 'sou', 'Soup'
    SIDE_DISH = 'sid', 'Side Dish'
    SALAD = 'sal', 'Salad'
