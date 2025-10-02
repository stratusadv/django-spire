from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing_extensions import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from django_spire.file.models import File
from django_spire.file.utils import random_64_char_token

if TYPE_CHECKING:
    from django.core.files.uploadedfile import InMemoryUploadedFile
    from django_spire.file.mixins import FileModelMixin


@dataclass
class FileFormatter:
    file: InMemoryUploadedFile
    related_field: str = None
    name: str = ...
    type: str = ...
    app_name: str = 'Uncategorized'

    def __post_init__(self):
        self.name = self._format_name()
        self.type = self._parse_type()

    def _format_name(self) -> str:
        return self.file.name.rsplit('.', 1)[0]

    def _parse_type(self) -> str:
        return self.file.name.rsplit('.', 1)[1]

    @property
    def location(self) -> str:
        location = 'django-spire/'

        if self.related_field is not None:
            location += str(self.related_field) + '/'

        location += str(self.app_name) + '/'
        location += random_64_char_token() + '/'
        location += self.name

        return location

    def null_file_obj(self) -> File:
        return File(
            file=self.file,
            name=self.name,
            size=self.size_verbose(),
            type=self.type,
            related_field=self.related_field
        )

    def size_verbose(self) -> str:
        if self.file.size < 512000:
            value = round(self.file.size / 1000, 2)
            ext = ' kb'
        elif self.file.size < 512000 * 1000:
            value = round(self.file.size / 1000000, 2)
            ext = ' Mb'
        elif self.file.size < 512000 * 1000 * 1000:
            value = round(self.file.size / 1000000000, 2)
            ext = ' Gb'
        else:
            value = ''
            ext = '>1.00 Tb'

        return str(value) + ext


@dataclass
class FileContentObjectFormatter(FileFormatter):
    content_object: FileModelMixin = ...

    @property
    def location(self) -> str:
        return 'django-spire/' + '/' + str(self.content_object._meta.app_label) + '/' + random_64_char_token() + '/' + self.name

    def null_file_obj(self) -> File:
        return File(
            content_type=ContentType.objects.get_for_model(self.content_object),
            object_id=self.content_object.id,
            file=self.file,
            name=self.name,
            size=self.size_verbose(),
            type=self.type,
            related_field=self.related_field
        )


@dataclass
class FileUploader(ABC):
    related_field: str | None
    app_name: str = 'Uncategorized'

    def null_file_obj(self, file):
        formatted_file = FileFormatter(
            file=file,
            related_field=self.related_field,
            app_name=self.app_name
        )
        return formatted_file.null_file_obj()

    @abstractmethod
    def upload(self, *args, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    def upload_from_form_field(self, *args, **kwargs) -> None:
        raise NotImplementedError


@dataclass
class SingleFileUploader(FileUploader):
    def upload(self, file: InMemoryUploadedFile) -> File:
        file = self.null_file_obj(file)
        file.save()
        return file

    def delete_old_files(self, content_object: FileModelMixin):
        old_files = content_object.files.active().related_field(self.related_field)

        for file in old_files:
            file.is_deleted = True
            file.is_active = False

        File.objects.bulk_update(old_files, ['is_active', 'is_deleted'])

    def upload_from_form_field(
        self,
        form_data,
        content_object: FileModelMixin
    ) -> File:
        try:
            return content_object.files.get(id=form_data['id'])
        except ObjectDoesNotExist:
            self.delete_old_files(content_object)
            file = File.objects.get(id=form_data['id'])
            file.content_type = ContentType.objects.get_for_model(content_object.__class__)
            file.object_id = content_object.id
            file.related_field = self.related_field
            return file.save()


@dataclass
class MultiFileUploader(FileUploader):
    def upload(self, files: list[InMemoryUploadedFile]) -> list[File]:
        files_to_upload = [self.null_file_obj(file) for file in files]
        return File.objects.bulk_create(files_to_upload)

    def upload_from_form_field(
        self,
        form_data: list[dict],
        content_object: FileModelMixin
    ) -> list[File]:
        file_ids = [file['id'] for file in form_data]

        # Delete files that are no longer in the form data
        old_files = (
            content_object
            .files
            .active()
            .related_field(self.related_field)
            .exclude(id__in=file_ids)
        )

        for old_file in old_files:
            old_file.is_deleted = True
            old_file.is_active = False

        File.objects.bulk_update(old_files, ['is_active', 'is_deleted'])

        link_files = File.objects.filter(id__in=file_ids, object_id__isnull=True)
        content_type = ContentType.objects.get_for_model(content_object.__class__)

        for link_file in link_files:
            link_file.content_type = content_type
            link_file.object_id = content_object.id
            link_file.related_field = self.related_field

        File.objects.bulk_update(
            link_files,
            fields=['content_type', 'object_id', 'related_field']
        )

        return content_object.files.active().related_field(self.related_field)
