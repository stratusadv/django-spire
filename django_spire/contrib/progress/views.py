from __future__ import annotations

import json
import time

from typing import TYPE_CHECKING

from django.http import StreamingHttpResponse

from django_spire.contrib.progress.tracker import ProgressTracker

if TYPE_CHECKING:
    from typing import Callable


def sse_stream_view(
    key: str,
    interval: float = 0.5,
    should_continue: Callable[[dict], bool] | None = None
) -> StreamingHttpResponse:
    def event_stream() -> None:
        tracker = ProgressTracker(key)
        previous_progress = -1

        while True:
            time.sleep(interval)
            data = tracker.get()

            if data:
                current_progress = data.get('progress', 0)

                if current_progress != previous_progress:
                    yield f'data: {json.dumps(data)}\n\n'
                    previous_progress = current_progress

                if should_continue and not should_continue(data):
                        break

                if current_progress >= 100 or data.get('step') == 'error':
                    break

    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )

    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'

    return response
