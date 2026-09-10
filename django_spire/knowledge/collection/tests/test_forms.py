from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory
from django.urls import reverse
from django_glue.enums import MessageLevel
from django_glue.message import GlueMessage

from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.forms import CollectionForm
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.collection.tests.factories import (
    create_test_auth_group,
    create_test_collection,
    create_test_collection_group,
)

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest

    from django_spire.auth.user.models import AuthUser


class CollectionFormTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.request_factory = RequestFactory()
        self.collection = create_test_collection()
        self.auth_group_1 = create_test_auth_group(name='Group 1')
        self.auth_group_2 = create_test_auth_group(name='Group 2')

        content_type = ContentType.objects.get_for_model(Collection)
        self.change_groups_permission = Permission.objects.get(
            codename='can_change_collection_groups', content_type=content_type
        )

    def _request(self, user: AuthUser) -> WSGIRequest:
        request = self.request_factory.get('/')
        request.user = user
        return request

    def _user_with_permission(self) -> AuthUser:
        user = create_user(username='collection_form_user')
        user.user_permissions.add(self.change_groups_permission)
        return type(user).objects.get(pk=user.pk)

    @staticmethod
    def _form_data(**kwargs: Any) -> dict[str, Any]:
        data = {
            'name': 'Video Game Cheat Codes',
            'description': 'A collection of video game cheat codes.',
            'parent': '',
        }
        data.update(kwargs)
        return data

    def test_form_has_groups_field(self):
        assert 'groups' in CollectionForm().fields

    def test_form_excludes_order(self):
        assert 'order' not in CollectionForm().fields

    def test_groups_initial_from_instance(self):
        create_test_collection_group(collection=self.collection, auth_group=self.auth_group_1)
        create_test_collection_group(collection=self.collection, auth_group=self.auth_group_2)

        form = CollectionForm(instance=self.collection)

        assert set(form.fields['groups'].initial) == {
            self.auth_group_1.pk,
            self.auth_group_2.pk,
        }

    def test_groups_initial_empty_for_new_collection(self):
        assert CollectionForm().fields['groups'].initial is None

    def test_save_model_obj_assigns_groups(self):
        form = CollectionForm(
            data=self._form_data(groups=[self.auth_group_1.pk, self.auth_group_2.pk]),
            instance=self.collection,
        )

        response = form.save_model_obj(self._request(self._user_with_permission()))

        assert response.status == 200
        assert set(self.collection.groups.values_list('auth_group_id', flat=True)) == {
            self.auth_group_1.pk,
            self.auth_group_2.pk,
        }

    def test_save_model_obj_replaces_existing_groups(self):
        create_test_collection_group(collection=self.collection, auth_group=self.auth_group_1)

        form = CollectionForm(
            data=self._form_data(groups=[self.auth_group_2.pk]), instance=self.collection
        )
        form.save_model_obj(self._request(self._user_with_permission()))

        assert list(self.collection.groups.values_list('auth_group_id', flat=True)) == [
            self.auth_group_2.pk
        ]

    def test_save_model_obj_empty_selection_clears_groups(self):
        create_test_collection_group(collection=self.collection, auth_group=self.auth_group_1)

        form = CollectionForm(data=self._form_data(groups=[]), instance=self.collection)
        form.save_model_obj(self._request(self._user_with_permission()))

        assert self.collection.groups.count() == 0

    def test_save_model_obj_without_permission_leaves_groups_untouched(self):
        create_test_collection_group(collection=self.collection, auth_group=self.auth_group_1)

        user = create_user(username='collection_form_no_perm_user')
        form = CollectionForm(
            data=self._form_data(groups=[self.auth_group_2.pk]), instance=self.collection
        )
        form.save_model_obj(self._request(user))

        assert list(self.collection.groups.values_list('auth_group_id', flat=True)) == [
            self.auth_group_1.pk
        ]

    def test_save_model_obj_redirects_to_home(self):
        form = CollectionForm(data=self._form_data(), instance=self.collection)

        response = form.save_model_obj(self._request(self.super_user))

        assert response.result == {
            'redirect': {'url': reverse('django_spire:knowledge:page:home')}
        }

    def test_parent_field_is_not_required(self):
        assert CollectionForm().fields['parent'].required is False

    def test_save_model_obj_without_parent_saves_null_parent(self):
        form = CollectionForm(data=self._form_data(), instance=self.collection)

        response = form.save_model_obj(self._request(self.super_user))
        self.collection.refresh_from_db()

        assert response.status == 200
        assert self.collection.parent_id is None

    def test_save_model_obj_clears_existing_parent(self):
        child = create_test_collection(parent=self.collection, name='Child Collection')

        form = CollectionForm(data=self._form_data(name='Child Collection'), instance=child)
        form.save_model_obj(self._request(self.super_user))
        child.refresh_from_db()

        assert child.parent_id is None

    def test_save_model_obj_redirects_to_parent(self):
        child = create_test_collection(parent=self.collection, name='Child Collection')

        form = CollectionForm(
            data=self._form_data(parent=self.collection.pk, name='Child Collection'),
            instance=child,
        )

        response = form.save_model_obj(self._request(self.super_user))

        assert response.result == {
            'redirect': {
                'url': reverse(
                    'django_spire:knowledge:collection:page:top_level',
                    kwargs={'pk': self.collection.pk},
                )
            }
        }

    def test_save_model_obj_invalid_form_returns_error_message(self):
        form = CollectionForm(data=self._form_data(name=''), instance=self.collection)

        response = form.save_model_obj(self._request(self.super_user))

        assert response.messages == [
            GlueMessage(level=MessageLevel.ERROR, message='Invalid Fields')
        ]
