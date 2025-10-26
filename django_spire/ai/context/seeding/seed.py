from django_spire.ai.context import models
from django_spire.ai.context import choices

from faker import Faker

models.Organization.objects.create(
    name='Spire Candy',
    legal_name='Spire Candy Processors Limited',
)

for people_role_choice in choices.PeopleRoleChoices:
    first_name = Faker().first_name()
    last_name = Faker().last_name()

    people = models.People.objects.create(
        role=people_role_choice.value,
        first_name=first_name,
        last_name=last_name,
        email=f'{first_name.lower()}.{last_name.lower()}@spirecandy.ca',
        phone=Faker().phone_number(),
    )