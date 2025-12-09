from __future__ import annotations

import pytest

from django.core.exceptions import ValidationError

from django_spire.ai.context.choices import PersonRoleChoices
from django_spire.ai.context.intelligence.prompts.organization_prompts import organization_info_prompt
from django_spire.ai.context.models import Organization, Person
from django_spire.core.tests.test_cases import BaseTestCase


class OrganizationModelTests(BaseTestCase):
    def test_organization_creation(self) -> None:
        org = Organization.objects.create(
            name='Test Organization',
            legal_name='Test Organization Inc.'
        )

        assert org.name == 'Test Organization'
        assert org.legal_name == 'Test Organization Inc.'

    def test_organization_only_one_allowed(self) -> None:
        Organization.objects.create(name='First Org')

        with pytest.raises(ValidationError):
            Organization.objects.create(name='Second Org')

    def test_organization_all_fields(self) -> None:
        org = Organization.objects.create(
            name='Test Org',
            legal_name='Test Org LLC',
            description='A test organization',
            sector='Technology',
            sub_sector='Software',
            website='https://example.com',
            street_address='123 Main St',
            unit_number='Suite 100',
            city='New York',
            province='NY',
            postal_code='10001',
            country='USA',
            phone='555-1234',
            email='info@example.com'
        )

        assert org.name == 'Test Org'
        assert org.sector == 'Technology'
        assert org.city == 'New York'
        assert org.email == 'info@example.com'

    def test_organization_nullable_fields(self) -> None:
        org = Organization.objects.create()

        assert org.name is None
        assert org.legal_name is None
        assert org.description is None

    def test_organization_get_only_or_none_exists(self) -> None:
        Organization.objects.create(name='Test Org')

        result = Organization.objects.get_only_or_none()

        assert result is not None
        assert result.name == 'Test Org'

    def test_organization_get_only_or_none_not_exists(self) -> None:
        result = Organization.objects.get_only_or_none()

        assert result is None


class PersonModelTests(BaseTestCase):
    def test_person_creation(self) -> None:
        person = Person.objects.create(
            first_name='John',
            last_name='Doe',
            role=PersonRoleChoices.ADMIN
        )

        assert person.first_name == 'John'
        assert person.last_name == 'Doe'
        assert person.role == PersonRoleChoices.ADMIN

    def test_person_default_role(self) -> None:
        person = Person.objects.create(
            first_name='Jane',
            last_name='Smith'
        )

        assert person.role == PersonRoleChoices.ADMIN

    def test_person_default_is_internal(self) -> None:
        person = Person.objects.create(
            first_name='Test',
            last_name='User'
        )

        assert person.is_internal_to_organization is True

    def test_person_all_roles(self) -> None:
        for role_choice in PersonRoleChoices:
            person = Person.objects.create(
                first_name=f'Test_{role_choice.value}',
                last_name='User',
                role=role_choice
            )

            assert person.role == role_choice

    def test_person_with_user(self) -> None:
        person = Person.objects.create(
            user=self.super_user,
            first_name='Super',
            last_name='User'
        )

        assert person.user == self.super_user

    def test_person_nullable_fields(self) -> None:
        person = Person.objects.create()

        assert person.first_name is None
        assert person.last_name is None
        assert person.phone is None
        assert person.email is None
        assert person.role_details is None

    def test_person_external_to_organization(self) -> None:
        person = Person.objects.create(
            first_name='External',
            last_name='Person',
            is_internal_to_organization=False
        )

        assert person.is_internal_to_organization is False


class PersonRoleChoicesTests(BaseTestCase):
    def test_admin_choice(self) -> None:
        assert PersonRoleChoices.ADMIN.value == 'admin'
        assert PersonRoleChoices.ADMIN.label == 'Admin'

    def test_human_resources_choice(self) -> None:
        assert PersonRoleChoices.HUMAN_RESOURCES.value == 'human_resources'
        assert PersonRoleChoices.HUMAN_RESOURCES.label == 'Human Resources'

    def test_sales_choice(self) -> None:
        assert PersonRoleChoices.SALES.value == 'sales'
        assert PersonRoleChoices.SALES.label == 'Sales'

    def test_manager_choice(self) -> None:
        assert PersonRoleChoices.MANAGER.value == 'manager'
        assert PersonRoleChoices.MANAGER.label == 'Manager'

    def test_marketing_choice(self) -> None:
        assert PersonRoleChoices.MARKETING.value == 'marketing'
        assert PersonRoleChoices.MARKETING.label == 'Marketing'

    def test_technical_choice(self) -> None:
        assert PersonRoleChoices.TECHNICAL.value == 'technical'
        assert PersonRoleChoices.TECHNICAL.label == 'Technical'

    def test_it_support_choice(self) -> None:
        assert PersonRoleChoices.IT_SUPPORT.value == 'it_support'
        assert PersonRoleChoices.IT_SUPPORT.label == 'IT Support'

    def test_all_choices_count(self) -> None:
        assert len(PersonRoleChoices) == 7


class OrganizationPromptTests(BaseTestCase):
    def test_organization_info_prompt_with_org(self) -> None:
        Organization.objects.create(
            name='Test Org',
            legal_name='Test Org Inc.'
        )

        prompt = organization_info_prompt()

        assert prompt is not None
        assert 'Organization Information' in prompt.to_str()

    def test_organization_info_prompt_without_org(self) -> None:
        prompt = organization_info_prompt()

        assert prompt is not None
        assert 'no organization information available' in prompt.to_str()
