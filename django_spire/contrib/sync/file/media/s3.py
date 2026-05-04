from __future__ import annotations

import logging

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

    def download(self, key: str, target_path: Path) -> None:
        target_path.parent.mkdir(parents=True, exist_ok=True)

        retry(
            lambda: self._client.download_file(
                self._bucket,
                key,
                str(target_path),
            ),
            attempts=self._retries,
            delay=self._retry_delay,
            exceptions=(BotoCoreError, OSError),
        )

        logger.info('Downloaded %s -> %s', key, target_path)

    def list_keys(self, prefix: str) -> set[str]:
        keys = set()
        continuation_token = None

        while True:
            kwargs = {
                'Bucket': self._bucket,
                'Prefix': prefix,
            }

            if continuation_token:
                kwargs['ContinuationToken'] = continuation_token

            response = self._client.list_objects_v2(**kwargs)

            for obj in response.get('Contents', []):
                keys.add(obj['Key'])

            if not response.get('IsTruncated'):
                break

            continuation_token = response['NextContinuationToken']

        return keys

    def upload(
        self,
        key: str,
        source_path: Path,
        content_type: str | None = None,
    ) -> str:
        extra_args = {'ACL': 'public-read'}

        if content_type:
            extra_args['ContentType'] = content_type

        retry(
            lambda: self._client.upload_file(
                str(source_path),
                self._bucket,
                key,
                ExtraArgs=extra_args,
            ),
            attempts=self._retries,
            delay=self._retry_delay,
            exceptions=(BotoCoreError, OSError),
        )

        logger.info('Uploaded %s -> %s/%s', source_path, self._bucket, key)

        return key
