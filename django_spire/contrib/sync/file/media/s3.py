from __future__ import annotations

import logging
import mimetypes

import boto3

from botocore.config import Config
from botocore.exceptions import BotoCoreError
from typing import TYPE_CHECKING

from django_spire.contrib.sync.file.media.base import Store
from django_spire.contrib.sync.core.retry import retry

if TYPE_CHECKING:
    from pathlib import Path


logger = logging.getLogger(__name__)


class S3Store(Store):
    def __init__(
        self,
        bucket: str,
        endpoint_url: str,
        region_name: str,
        access_key: str,
        secret_key: str,
        retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        self._bucket = bucket
        self._retries = retries
        self._retry_delay = retry_delay
        self._client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            region_name=region_name,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4'),
        )

    def upload(
        self,
        key: str,
        source_path: Path,
        content_type: str | None = None,
    ) -> str:
        if content_type is None:
            content_type, _ = mimetypes.guess_type(source_path.name)

        extra: dict[str, str] = {}

        if content_type:
            extra['ContentType'] = content_type

        retry(
            lambda: self._client.upload_file(
                str(source_path),
                self._bucket,
                key,
                ExtraArgs=extra,
            ),
            attempts=self._retries,
            delay=self._retry_delay,
            exceptions=(BotoCoreError, OSError),
        )

        logger.info('Uploaded %s -> %s', source_path, key)
        return key
