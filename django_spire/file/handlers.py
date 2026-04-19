from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType

from django_spire.file.interfaces import SingleFileUploader

if TYPE_CHECKING:
    from django.core.files.uploadedfile import InMemoryUploadedFile

    from django_spire.file.mixins import FileModelMixin
    from django_spire.file.models import File


@dataclass
class SingleFileHandler:
    related_field: str
    _uploader: SingleFileUploader = field(init=False)

    def __post_init__(self) -> None:
        self._uploader = SingleFileUploader(related_field=self.related_field)

    def save(self, data: dict | InMemoryUploadedFile | None, instance: FileModelMixin) -> File | None:
        if data is None:
            return None

        if isinstance(data, dict):
            return self._save_from_metadata(data, instance)

        if hasattr(data, 'read'):
            return self._save_from_upload(data, instance)

        return None

    def _save_from_metadata(self, data: dict, instance: FileModelMixin) -> File | None:
        if not data.get('id') or data.get('id') == 0:
            return None

        return self._uploader.upload_from_form_field(data, instance)

    def _save_from_upload(self, file: InMemoryUploadedFile, instance: FileModelMixin) -> File:
        self._uploader.delete_old_files(instance)

        uploaded = self._uploader.upload(file)
        uploaded.content_type = ContentType.objects.get_for_model(instance)
        uploaded.object_id = instance.id
        uploaded.save()

        return uploaded
