from __future__ import annotations

import pytest

from abc import ABC

from django.contrib.auth.models import User
from django.test import TestCase

from django_spire.contrib.constructor import (
    BaseConstructor,
    BaseDjangoModelConstructor,
    ConstructorError,
)


class TestBaseConstructor(TestCase):
    def test_abc_subclass_does_not_require_obj_annotation(self) -> None:
        class AbstractConstructor(BaseConstructor, ABC):
            pass

        # Should not raise
        assert AbstractConstructor is not None

    def test_constructor_with_none_obj(self) -> None:
        class StringConstructor(BaseConstructor[str]):
            obj: str

        constructor = StringConstructor(None)

        assert not hasattr(constructor, 'obj')

    def test_constructor_with_valid_obj(self) -> None:
        class StringConstructor(BaseConstructor[str]):
            obj: str

        constructor = StringConstructor('test')

        assert constructor.obj == 'test'

    def test_constructor_with_wrong_type_raises_error(self) -> None:
        class StringConstructor(BaseConstructor[str]):
            obj: str

        with pytest.raises(ConstructorError):
            StringConstructor(123)

    def test_obj_class_property(self) -> None:
        class StringConstructor(BaseConstructor[str]):
            obj: str

        constructor = StringConstructor('test')

        assert constructor.obj_class is str

    def test_obj_is_valid_property(self) -> None:
        class StringConstructor(BaseConstructor[str]):
            obj: str

        constructor = StringConstructor('test')

        assert constructor._obj_is_valid is True

    def test_post_init_called(self) -> None:
        class StringConstructor(BaseConstructor[str]):
            obj: str
            post_init_called: bool = False

            def __post_init__(self):
                self.post_init_called = True

        constructor = StringConstructor('test')

        assert constructor.post_init_called is True

    def test_subclass_without_obj_annotation_raises_error(self) -> None:
        with pytest.raises(ConstructorError, match='must have an "obj" attribute'):
            class InvalidConstructor(BaseConstructor[str]):
                pass


class TestBaseDjangoModelConstructor(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'  # noqa: S106
        )

    def test_constructor_with_django_model(self) -> None:
        class UserConstructor(BaseDjangoModelConstructor[User]):
            obj: User

        constructor = UserConstructor(self.user)

        assert constructor.obj == self.user

    def test_model_obj_is_created_true(self) -> None:
        class UserConstructor(BaseDjangoModelConstructor[User]):
            obj: User

        constructor = UserConstructor(self.user)

        assert constructor.model_obj_is_created is True

    def test_model_obj_is_created_false_for_new(self) -> None:
        class UserConstructor(BaseDjangoModelConstructor[User]):
            obj: User

        new_user = User(username='newuser')
        constructor = UserConstructor(new_user)

        assert constructor.model_obj_is_created is False

    def test_model_obj_is_new_false(self) -> None:
        class UserConstructor(BaseDjangoModelConstructor[User]):
            obj: User

        constructor = UserConstructor(self.user)

        assert constructor.model_obj_is_new is False

    def test_model_obj_is_new_true(self) -> None:
        class UserConstructor(BaseDjangoModelConstructor[User]):
            obj: User

        new_user = User(username='newuser')
        constructor = UserConstructor(new_user)

        assert constructor.model_obj_is_new is True

    def test_model_obj_pk_is_empty_true(self) -> None:
        class UserConstructor(BaseDjangoModelConstructor[User]):
            obj: User

        new_user = User(username='newuser')
        constructor = UserConstructor(new_user)

        assert constructor._model_obj_pk_is_empty is True

    def test_model_obj_pk_is_empty_false(self) -> None:
        class UserConstructor(BaseDjangoModelConstructor[User]):
            obj: User

        constructor = UserConstructor(self.user)

        assert constructor._model_obj_pk_is_empty is False

    def test_obj_class_returns_model_class(self) -> None:
        class UserConstructor(BaseDjangoModelConstructor[User]):
            obj: User

        constructor = UserConstructor(self.user)

        assert constructor.obj_class is User

    def test_obj_is_valid_true(self) -> None:
        class UserConstructor(BaseDjangoModelConstructor[User]):
            obj: User

        constructor = UserConstructor(self.user)

        assert constructor._obj_is_valid is True


class TestConstructorError(TestCase):
    def test_constructor_error_is_exception(self) -> None:
        assert issubclass(ConstructorError, Exception)

    def test_constructor_error_message(self) -> None:
        error = ConstructorError('Test error message')

        assert str(error) == 'Test error message'

    def test_constructor_error_can_be_raised(self) -> None:
        with pytest.raises(ConstructorError):
            message = 'Test'
            raise ConstructorError(message)


class TestConstructorDescriptor(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'  # noqa: S106
        )

    def test_descriptor_get_from_model_instance(self) -> None:
        class UserConstructor(BaseDjangoModelConstructor[User]):
            obj: User

        constructor = UserConstructor(self.user)

        assert constructor.obj == self.user
