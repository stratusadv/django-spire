from __future__ import annotations

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.collection.tests.factories import create_test_collection


class CollectionFormViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.collection = create_test_collection()
        self.child_collection = create_test_collection(
            parent=self.collection, name='Child Collection'
        )

    @staticmethod
    def _breadcrumb_names(response) -> list[str]:
        return [
            breadcrumb.name
            for breadcrumb in response.context['django_spire_navigation']['breadcrumbs']
        ]

    def _create_url(self) -> str:
        return reverse('django_spire:knowledge:collection:form:create')

    def _create_with_parent_url(self, parent_pk: int) -> str:
        return reverse(
            'django_spire:knowledge:collection:form:create_with_parent',
            kwargs={'parent_pk': parent_pk},
        )

    def _update_url(self, pk: int) -> str:
        return reverse('django_spire:knowledge:collection:form:update', kwargs={'pk': pk})

    def test_create_view_uses_form_page_template(self):
        response = self.client.get(self._create_url())

        assert response.status_code == 200
        self.assertTemplateUsed(response, 'django_spire/knowledge/collection/page/form_page.html')

    def test_create_view_context_collection_is_unsaved(self):
        response = self.client.get(self._create_url())

        assert response.context['collection'].pk is None
        assert response.context['collection_parent_pk'] is None

    def test_create_view_page_title_and_breadcrumbs(self):
        response = self.client.get(self._create_url())

        assert response.context['django_spire_navigation']['page_title'] == 'Collection'
        assert self._breadcrumb_names(response)[-1] == 'Create'

    def test_create_with_parent_view_sets_parent_pk_in_context(self):
        response = self.client.get(self._create_with_parent_url(self.collection.pk))

        assert response.status_code == 200
        assert response.context['collection_parent_pk'] == self.collection.pk

    def test_create_with_parent_view_breadcrumbs_include_parent_chain(self):
        response = self.client.get(self._create_with_parent_url(self.child_collection.pk))

        breadcrumb_names = self._breadcrumb_names(response)

        assert self.collection.name in breadcrumb_names
        assert self.child_collection.name in breadcrumb_names
        assert breadcrumb_names[-1] == 'Create'

    def test_update_view_context_collection_is_instance(self):
        response = self.client.get(self._update_url(self.collection.pk))

        assert response.status_code == 200
        assert response.context['collection'].pk == self.collection.pk

    def test_update_view_breadcrumbs_include_collection_and_edit(self):
        response = self.client.get(self._update_url(self.child_collection.pk))

        breadcrumb_names = self._breadcrumb_names(response)

        assert self.collection.name in breadcrumb_names
        assert breadcrumb_names[-2] == self.child_collection.name
        assert breadcrumb_names[-1] == 'Edit'

    def test_view_registers_glue_collection_form(self):
        response = self.client.get(self._update_url(self.collection.pk))

        assert 'collection_form' in response.content.decode()

    def test_view_renders_none_option_for_parent_field(self):
        response = self.client.get(self._create_url())

        assert '<option value="">None</option>' in response.content.decode()

    def test_top_level_query_param_hides_parent_field(self):
        response = self.client.get(self._create_url(), data={'top_level': 'True'})

        assert response.status_code == 200
        assert '<option value="">None</option>' not in response.content.decode()

    def test_view_does_not_create_a_collection(self):
        collection_count = Collection.objects.count()

        self.client.get(self._create_url())

        assert Collection.objects.count() == collection_count

    def test_view_requires_add_collection_permission(self):
        self.client.force_login(create_user(username='collection_form_view_user'))

        response = self.client.get(self._create_url())

        assert response.status_code == 403

    def test_view_allows_user_with_add_collection_permission(self):
        user = create_user(username='collection_form_view_permitted_user')
        user.user_permissions.add(
            Permission.objects.get(
                codename='add_collection',
                content_type=ContentType.objects.get_for_model(Collection),
            )
        )
        self.client.force_login(type(user).objects.get(pk=user.pk))

        response = self.client.get(self._create_url())

        assert response.status_code == 200
