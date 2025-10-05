from __future__ import annotations

from django_spire.ai.prompt.bots import DandyPythonPromptBot


def text_to_prompt_cli(prompt: str):
    bot = DandyPythonPromptBot()
    bot.process(prompt)
