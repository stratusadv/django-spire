from __future__ import annotations

import logging

import paramiko

from typing import Callable, TYPE_CHECKING

from django_spire.contrib.sync.retry import retry
from django_spire.contrib.sync.source.base import Source

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Self


logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30


class SFTPSource(Source):
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str | None = None,
        key_path: str | None = None,
        key_passphrase: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._key_path = key_path
        self._key_passphrase = key_passphrase
        self._timeout = timeout
        self._retries = retries
        self._retry_delay = retry_delay
        self._transport: paramiko.Transport | None = None
        self._sftp: paramiko.SFTPClient | None = None

    def _require_connection(self) -> paramiko.SFTPClient:
        if self._sftp is None:
            msg = (
                f'Not connected to SFTP {self._host}:{self._port}. '
                f'Call connect() or use as a context manager.'
            )
            raise RuntimeError(msg)

        return self._sftp

    def _load_key(self) -> paramiko.PKey:
        key_classes = (
            paramiko.Ed25519Key,
            paramiko.RSAKey,
            paramiko.ECDSAKey,
        )

        last_exc: paramiko.SSHException | None = None

        for cls in key_classes:
            try:
                return cls.from_private_key_file(
                    self._key_path,
                    password=self._key_passphrase,
                )
            except paramiko.PasswordRequiredException:
                raise
            except paramiko.SSHException as exc:
                logger.debug(
                    'Key type %s failed for %s: %s',
                    cls.__name__,
                    self._key_path,
                    exc,
                )
                last_exc = exc
                continue

        message = f'Unable to load private key from {self._key_path}'
        raise paramiko.SSHException(message) from last_exc

    def connect(self) -> None:
        sock = (self._host, self._port)
        self._transport = paramiko.Transport(sock)

        if self._key_path:
            key = self._load_key()
            self._transport.connect(username=self._username, pkey=key)
        else:
            self._transport.connect(
                username=self._username,
                password=self._password,
            )

        self._transport.set_keepalive(int(self._timeout))
        self._sftp = paramiko.SFTPClient.from_transport(self._transport)
        self._sftp.get_channel().settimeout(self._timeout)

        logger.info('Connected to SFTP %s:%d', self._host, self._port)

    def close(self) -> None:
        if self._sftp:
            self._sftp.close()
        if self._transport:
            self._transport.close()

        self._sftp = None
        self._transport = None

        logger.info('Disconnected from SFTP')

    def __enter__(self) -> Self:
        self.connect()
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def download(
        self,
        remote_path: str,
        local_path: Path,
        callback: Callable[[int, int], None] | None = None,
    ) -> None:
        sftp = self._require_connection()
        local_path.parent.mkdir(parents=True, exist_ok=True)

        retry(
            lambda: sftp.get(remote_path, str(local_path), callback=callback),
            attempts=self._retries,
            delay=self._retry_delay,
            exceptions=(IOError, paramiko.SSHException),
        )

        logger.info('Downloaded %s -> %s', remote_path, local_path)

    def list_dir(self, remote_path: str) -> list[str]:
        sftp = self._require_connection()
        return sftp.listdir(remote_path)
