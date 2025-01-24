from __future__ import annotations

import whisper

from enum import Enum
from pathlib import Path

from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect


class WhisperModel(Enum):
    TINY = 'tiny'
    BASE = 'base'
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'
    TURBO = 'turbo'


model = whisper.load_model(WhisperModel.TINY.value)


@csrf_protect
def transcribe_audio(request):
    if request.method == 'POST':
        file = request.FILES.get('audio')

        if not file:
            return JsonResponse({'error': 'No audio file provided'}, status=400)

        storage = FileSystemStorage()
        location = storage.save(file.name, file)
        path = Path(storage.path(location))

        try:
            result = model.transcribe(str(path))
            transcription = result['text']
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            if path.exists():
                path.unlink()

        return JsonResponse({'transcription': transcription}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
