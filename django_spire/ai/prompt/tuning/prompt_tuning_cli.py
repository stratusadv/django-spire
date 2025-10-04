from __future__ import annotations

from dandy.recorder import Recorder

from django_spire.ai.prompt.bots import DandyPythonPromptBot
from django_spire.ai.prompt.tuning.bots import SimplePromptTuningBot


def prompt_tuning_cli(prompt: str):
    Recorder.start_recording(recording_name='prompt_tuning')

    holding = prompt
    tuning_bot = SimplePromptTuningBot()

    print('----------------------------------------------------')

    while True:
        print("\nEnter your feedback (or type 'stop' to finish):")
        feedback = input()

        if feedback == "stop":
            break

        print('Attempting to tune prompt.....')

        new_prompt = tuning_bot.process(holding, feedback)
        holding = new_prompt.prompt

        print('----------------------NEW PROMPT START------------------------------')
        print()
        print(new_prompt.prompt)
        print()
        print('----------------------NEW PROMPT END------------------------------')
        print()

    Recorder.stop_recording(recording_name='prompt_tuning')
    Recorder.to_html_file(recording_name='prompt_tuning')

    python_bot = DandyPythonPromptBot()
    python_bot.process(prompt)
