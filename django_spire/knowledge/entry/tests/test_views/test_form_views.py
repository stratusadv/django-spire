from __future__ import annotations

import json
import re

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.collection.tests.factories import create_test_collection
from django_spire.knowledge.entry.models import Entry
from django_spire.knowledge.entry.tests.factories import create_test_entry


class EntryFormViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.collection = create_test_collection()
        self.child_collection = create_test_collection(
            parent=self.collection, name='Child Collection'
        )
        self.entry = create_test_entry(collection=self.child_collection)

    @staticmethod
    def _breadcrumb_names(response) -> list[str]:
        return [
            breadcrumb.name
            for breadcrumb in response.context['django_spire_navigation']['breadcrumbs']
        ]

    @staticmethod
    def _glue_manifests(response) -> list[dict]:
        match = re.search(
            r'<script id="django-glue-context" type="application/json">(.*?)</script>',
            response.content.decode(),
            re.DOTALL,
        )

        return json.loads(match.group(1))['manifest_list']

    def _create_url(self, collection_pk: int | None = None) -> str:
        return reverse(
            'django_spire:knowledge:entry:form:create',
            kwargs={'collection_pk': collection_pk or self.collection.pk},
        )

    def _update_url(self, pk: int, collection_pk: int | None = None) -> str:
        return reverse(
            'django_spire:knowledge:entry:form:update',
            kwargs={'pk': pk, 'collection_pk': collection_pk or self.collection.pk},
        )

    def test_create_view_uses_form_page_template(self):
        response = self.client.get(self._create_url())

        assert response.status_code == 200
        self.assertTemplateUsed(response, 'django_spire/knowledge/entry/page/form_page.html')

    def test_create_view_context_entry_is_unsaved(self):
        response = self.client.get(self._create_url())

        assert response.context['entry'].pk is None
        assert response.context['form'].instance.pk is None

    def test_create_view_action_url_is_create_url(self):
        response = self.client.get(self._create_url())

        assert response.context['action_url'] == self._create_url()

    def test_create_view_breadcrumbs_include_collection_chain(self):
        response = self.client.get(self._create_url(self.child_collection.pk))

        breadcrumb_names = self._breadcrumb_names(response)

        assert self.collection.name in breadcrumb_names
        assert self.child_collection.name in breadcrumb_names

    def test_create_view_registers_glue_entry_model(self):
        response = self.client.get(self._create_url())

        manifest = self._glue_manifests(response)[0]
        attributes = manifest['metadata']['attributes']

        assert attributes['name']['namespace'] == 'field'
        assert attributes['save']['namespace'] == 'callable'

    def test_update_view_context_entry_is_instance(self):
        response = self.client.get(self._update_url(self.entry.pk, self.child_collection.pk))

        assert response.status_code == 200
        assert response.context['entry'].pk == self.entry.pk
        assert response.context['form'].initial['name'] == self.entry.name

    def test_update_view_action_url_is_update_url(self):
        response = self.client.get(self._update_url(self.entry.pk, self.child_collection.pk))

        assert response.context['action_url'] == self._update_url(
            self.entry.pk, self.child_collection.pk
        )

    def test_update_view_breadcrumbs_include_entry_name(self):
        response = self.client.get(self._update_url(self.entry.pk, self.child_collection.pk))

        assert self.entry.name in self._breadcrumb_names(response)

    def test_create_view_post_creates_entry_in_collection(self):
        response = self.client.post(self._create_url(), data={'name': 'Speedrun Glitches'})

        entry = Entry.objects.get(name='Speedrun Glitches')

        assert response.status_code == 302
        assert entry.collection_id == self.collection.pk

    def test_create_view_post_redirects_to_version_editor(self):
        response = self.client.post(self._create_url(), data={'name': 'Speedrun Glitches'})

        entry = Entry.objects.get(name='Speedrun Glitches')

        assert response.url == reverse(
            'django_spire:knowledge:entry:version:page:editor', kwargs={'pk': entry.pk}
        )

    def test_create_view_post_creates_current_version(self):
        self.client.post(self._create_url(), data={'name': 'Speedrun Glitches'})

        entry = Entry.objects.get(name='Speedrun Glitches')

        assert entry.current_version is not None
        assert entry.current_version.author_id == self.super_user.pk

    def test_update_view_post_renames_entry(self):
        response = self.client.post(
            self._update_url(self.entry.pk, self.child_collection.pk),
            data={'name': 'Renamed Entry'},
        )
        self.entry.refresh_from_db()

        assert response.status_code == 302
        assert self.entry.name == 'Renamed Entry'

    def test_create_view_post_with_invalid_data_does_not_create_entry(self):
        entry_count = Entry.objects.count()

        response = self.client.post(self._create_url(), data={'name': ''})

        assert response.status_code == 200
        assert Entry.objects.count() == entry_count

    def test_view_requires_add_collection_permission(self):
        self.client.force_login(create_user(username='entry_form_view_user'))

        response = self.client.get(self._create_url())

        assert response.status_code == 403

    def test_view_allows_user_with_add_collection_permission(self):
        user = create_user(username='entry_form_view_permitted_user')
        user.user_permissions.add(
            Permission.objects.get(
                codename='add_collection',
                content_type=ContentType.objects.get_for_model(Collection),
            )
        )
        self.client.force_login(type(user).objects.get(pk=user.pk))

        response = self.client.get(self._create_url())

        assert response.status_code == 200


class EntryImportFormViewTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.collection = create_test_collection()

    def _import_url(self, collection_pk: int | None = None) -> str:
        return reverse(
            'django_spire:knowledge:entry:form:import',
            kwargs={'collection_pk': collection_pk or self.collection.pk},
        )

    def test_import_view_uses_import_form_page_template(self):
        response = self.client.get(self._import_url())

        assert response.status_code == 200
        self.assertTemplateUsed(response, 'django_spire/knowledge/entry/page/import_form_page.html')

    def test_import_view_context_has_collection_pk(self):
        response = self.client.get(self._import_url())

        assert response.context['collection_pk'] == self.collection.pk

    def test_import_view_context_has_supported_file_types(self):
        response = self.client.get(self._import_url())

        assert response.context['supported_file_types'] == ['.md', '.docx']
        assert response.context['supported_file_types_verbose'] == '.md, .docx'

    def test_import_view_breadcrumbs_end_with_import_files(self):
        response = self.client.get(self._import_url())

        breadcrumb_names = [
            breadcrumb.name
            for breadcrumb in response.context['django_spire_navigation']['breadcrumbs']
        ]

        assert self.collection.name in breadcrumb_names
        assert breadcrumb_names[-1] == 'Import Files'

    def test_import_view_registers_glue_import_file_form(self):
        response = self.client.get(self._import_url())

        assert 'import_file_form' in response.content.decode()

    def test_import_view_requires_add_collection_permission(self):
        self.client.force_login(create_user(username='entry_import_form_view_user'))

        response = self.client.get(self._import_url())

        assert response.status_code == 403
