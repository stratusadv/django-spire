from __future__ import annotations

from pathlib import Path

from dandy.intel import BaseIntel
from django.conf import settings

_MARKDOWN_OUTPUT_PATH = Path(settings.BASE_DIR, '.markdown')
_PROMPT_OUTPUT_PATH = Path(settings.BASE_DIR, '.prompt_generator_output')


class DandyPromptPythonFileIntel(BaseIntel):
    source_code: str
    file_name: str

    def to_file(self):
        Path(_PROMPT_OUTPUT_PATH).mkdir(parents=True, exist_ok=True)

        with open(Path(_PROMPT_OUTPUT_PATH, self.file_name), 'w') as f:
            f.write(self.source_code)

        print(f'Done ... saved to "{Path(_PROMPT_OUTPUT_PATH, self.file_name)}"')


class TextToMarkdownIntel(BaseIntel):
    markdown_content: str
    file_name: str

    def to_file(self):
        Path(_MARKDOWN_OUTPUT_PATH).mkdir(parents=True, exist_ok=True)

        with open(Path(_MARKDOWN_OUTPUT_PATH, self.file_name), 'w') as f:
            f.write(self.markdown_content)

        print(f'Done ... saved to "{Path(_MARKDOWN_OUTPUT_PATH, self.file_name)}"')
