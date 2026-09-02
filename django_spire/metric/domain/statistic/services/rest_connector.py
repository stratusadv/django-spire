from __future__ import annotations

from django_spire.contrib.rest.connector.connector import BaseRestHttpConnector

_REMOTE_API_PATH = 'api/v1/metric/domain/statistic'


class SpireMetricRestConnector(BaseRestHttpConnector):
    base_url = 'https://localhost'
    max_retries = 2
    timeout = 10

    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url
        self.base_headers = {'X-API-Key': api_key, 'Content-Type': 'application/json'}
        super().__init__()

    def record(self, statistic_key: str, payload: dict) -> dict | None:
        return self.post(f'{_REMOTE_API_PATH}/{statistic_key}/record', json=payload).json()
