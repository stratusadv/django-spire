from __future__ import annotations


from django.core.exceptions import ImproperlyConfigured
import urllib.parse
from abc import ABC
from typing import TypeVar, overload, Generic, get_args, ForwardRef

import requests
from pydantic import BaseModel
from requests.auth import AuthBase

TDefaultResponseSchema = TypeVar('TDefaultResponseSchema', bound=BaseModel)
TResponseSchemaOverride = TypeVar('TResponseSchemaOverride', bound=BaseModel)

class BaseRestApiClient(ABC, Generic[TDefaultResponseSchema]):
    _base_url: str | None
    _rest_schema_class: type[TDefaultResponseSchema]
    _base_url_path: str = ''
    _base_headers: dict = {}

    def __init_subclass__(cls, **kwargs):
        required_attributes = ['_base_url']
        for attribute in required_attributes:
            if getattr(cls, attribute, None) is None:
                message = f'{attribute} is required'
                raise ImproperlyConfigured(message)

        cls._validate_url(cls._base_url)

    @staticmethod
    def _validate_url(url: str):
        try:
            urllib.parse.urlparse(url)
        except ValueError:
            raise ValueError('Configured url is not a valid url')

    @classmethod
    def _get_schema_class(cls) -> type[BaseModel]:
        """
        Lazily resolve and cache the schema class from the generic type parameter.
        This is called at runtime rather than class definition time, allowing
        forward references to be resolved after all classes are defined.
        """
        # Return cached value if already resolved
        if hasattr(cls, '_rest_schema_class') and cls._rest_schema_class is not None:
            return cls._rest_schema_class

        import sys

        for klass in cls.__mro__:
            if not hasattr(klass, '__orig_bases__'):
                continue
            for base in klass.__orig_bases__:
                args = get_args(base)
                if not args:
                    continue
                arg = args[0]
                # Handle ForwardRef (from `from __future__ import annotations` or string annotations)
                if isinstance(arg, ForwardRef):
                    # Get the string name from the ForwardRef
                    ref_name = arg.__forward_arg__
                    # Resolve from the module where the class is defined
                    module = sys.modules.get(klass.__module__, None)
                    if module and hasattr(module, ref_name):
                        arg = getattr(module, ref_name)
                # Handle plain string forward references
                elif isinstance(arg, str):
                    module = sys.modules.get(klass.__module__, None)
                    if module and hasattr(module, arg):
                        arg = getattr(module, arg)
                # Check if it's a concrete BaseModel subclass (not a TypeVar)
                if isinstance(arg, type) and issubclass(arg, BaseModel):
                    cls._rest_schema_class = arg
                    return arg

        raise ImproperlyConfigured(
            f"Could not resolve schema class for {cls.__name__}. "
            "Ensure the generic type parameter is a concrete BaseModel subclass."
        )

    @classmethod
    def _get_auth(cls) -> AuthBase | None:
        return None

    def __repr__(self):
        return f'{self.__class__.__name__}(base_url={self._base_url})'

    def _build_url(self, url_path: str | None = None) -> str:
        url = self._base_url
        if self._base_url_path:
            url = f'{url.rstrip("/")}/{self._base_url_path.lstrip("/")}'

        if url_path:
            url = f'{url.rstrip("/")}/{url_path.lstrip("/")}'

        self._validate_url(url)

        return url

    def _request(
        self,
        method: str = 'GET',
        url_path: str | None = None,
        headers: dict | None = None,
        *args,
        **kwargs,
    ) -> RestResponseData[TDefaultResponseSchema]:
        response = requests.request(
            method=method,
            url=self._build_url(url_path),
            auth=self._get_auth(),
            headers=headers or {},
            *args,
            **kwargs,
        )

        response.raise_for_status()

        return RestResponseData(self, response)

    def _get(
        self,
        url_path: str | None = None,
        headers: dict | None = None,
        *args,
        **kwargs,
    ) -> RestResponseData[TDefaultResponseSchema]:
        return self._request(
            method='GET',
            url_path=url_path,
            headers=headers,
            *args,
            **kwargs
        )

    def _post(
        self,
        url_path: str | None = None,
        headers: dict | None = None,
        *args,
        **kwargs,
    ) -> RestResponseData[TDefaultResponseSchema]:
        return self._request(
            method='POST',
            url_path=url_path,
            headers=headers,
            *args,
            **kwargs
        )

    def _put(
        self,
        url_path: str | None = None,
        headers: dict | None = None,
        *args,
        **kwargs,
    ) -> RestResponseData[TDefaultResponseSchema]:
        return self._request(
            method='PUT',
            url_path=url_path,
            headers=headers,
            *args,
            **kwargs
        )

    def _delete(
        self,
        url_path: str | None = None,
        headers: dict | None = None,
        *args,
        **kwargs,
    ) -> RestResponseData[TDefaultResponseSchema]:
        return self._request(
            method='DELETE',
            url_path=url_path,
            headers=headers,
            *args,
            **kwargs
        )

    def _patch(
        self,
        url_path: str | None = None,
        headers: dict | None = None,
        *args,
        **kwargs,
    ) -> RestResponseData[TDefaultResponseSchema]:
        return self._request(
            method='PATCH',
            url_path=url_path,
            headers=headers,
            *args,
            **kwargs
        )

    @overload
    def _response_to_single_obj(
        self,
        response: requests.Response,
        obj_class: type[TResponseSchemaOverride]
    ) -> TResponseSchemaOverride: ...

    @overload
    def _response_to_single_obj(
        self,
        response: requests.Response,
        obj_class: None = None
    ) -> TDefaultResponseSchema: ...

    def _response_to_single_obj(
        self,
        response: requests.Response,
        obj_class: type[TResponseSchemaOverride] | None = None
    ) -> TResponseSchemaOverride | TDefaultResponseSchema:
        obj_class = obj_class or self._get_schema_class()

        json_data = response.json()
        if not isinstance(json_data, dict):
            raise ValueError(
                'Trying to convert response data to a single object but response data is a list.')
        return obj_class(**json_data)

    @overload
    def _response_to_obj_list(
        self,
        response: requests.Response,
        obj_class: type[TResponseSchemaOverride]
    ) -> list[TResponseSchemaOverride]: ...

    @overload
    def _response_to_obj_list(
        self,
        response: requests.Response,
        obj_class: None = None
    ) -> list[TDefaultResponseSchema]: ...

    def _response_to_obj_list(
        self,
        response: requests.Response,
        obj_class: type[TResponseSchemaOverride] | None = None
    ) -> list[TResponseSchemaOverride] | list[TDefaultResponseSchema]:
        obj_class = obj_class or self._get_schema_class()

        json_data = response.json()
        if not isinstance(json_data, list):
            raise ValueError(
                'Trying to convert response data to a list of objects but response data is a single object.')
        return [obj_class(**item) for item in json_data]


class RestResponseData(Generic[TDefaultResponseSchema]):
    def __init__(self, client: BaseRestApiClient[TDefaultResponseSchema], response: requests.Response):
        self.response = response
        self.client = client

    @overload
    def to_single_obj(self, obj_class: type[TResponseSchemaOverride]) -> TResponseSchemaOverride: ...

    @overload
    def to_single_obj(self, obj_class: None = None) -> TDefaultResponseSchema: ...

    def to_single_obj(self, obj_class: type[TResponseSchemaOverride] | None = None) -> TResponseSchemaOverride | TDefaultResponseSchema:
        return self.client._response_to_single_obj(self.response, obj_class)

    @overload
    def to_obj_list(self, obj_class: type[TResponseSchemaOverride]) -> list[TResponseSchemaOverride]: ...

    @overload
    def to_obj_list(self, obj_class: None = None) -> list[TDefaultResponseSchema]: ...

    def to_obj_list(self, obj_class: type[TResponseSchemaOverride] | None = None) -> list[TResponseSchemaOverride] | list[TDefaultResponseSchema]:
        return self.client._response_to_obj_list(self.response, obj_class)