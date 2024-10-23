from django_spire.cookbook import models


def create_test_cookbook():
    return models.Cookbook.objects.create(
        name='Ratatouille',
        description='Theres a mouse in my hat',
    )
