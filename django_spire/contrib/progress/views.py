from __future__ import annotations

import json
import time

from typing import TYPE_CHECKING

from django.core.cache import cache
from django.http import StreamingHttpResponse

if TYPE_CHECKING:
    from typing import Callable, Generator


def sse_stream_view(
    key: str,
    interval: float = 0.5,
    should_continue: Callable[[dict], bool] | None = None,
    timeout: int = 300
) -> StreamingHttpResponse:
    cache_key = f'progress_tracker_{key}'

    def event_stream() -> Generator[str, None, None]:
        previous_data = None
        start_time = time.time()
        last_heartbeat = time.time()

        yield ': connected\n\n'

        while True:
            elapsed = time.time() - start_time

            if elapsed > timeout:
                yield f'data: {json.dumps({"step": "error", "message": "Timeout", "progress": 0})}\n\n'
                break

            data = cache.get(cache_key)

            if data and data != previous_data:
                yield f'data: {json.dumps(data)}\n\n'
                previous_data = data
                last_heartbeat = time.time()

                if should_continue and not should_continue(data):
                    break

                if data.get('progress', 0) >= 100 or data.get('step') == 'error':
                    break

            if time.time() - last_heartbeat > 10:
                yield ': heartbeat\n\n'
                last_heartbeat = time.time()

            time.sleep(interval)

    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )

    response['Cache-Control'] = 'no-cache, no-store'
    response['X-Accel-Buffering'] = 'no'

    return response
