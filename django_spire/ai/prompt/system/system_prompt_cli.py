from __future__ import annotations

from dandy import Recorder

from django_spire.ai.prompt.bots import DandyPythonPromptBot
from django_spire.ai.prompt.system import bots
from django_spire.ai.prompt.tuning.bots import SimplePromptTuningBot


def create_system_prompt_cli() -> None:
    Recorder.start_recording(recording_name='system_prompt')

    user_story = input('Enter your user story: ')

    bot = bots.SystemPromptBot()
    prompt = bot.process(user_story)
    print(prompt)

    tuning_bot = SimplePromptTuningBot()

    while True:
        print("\nEnter your feedback (or type 'stop' to finish):")
        feedback = input()

        if feedback == "stop":
            break

        print('Creating new prompt from feedback.....')
        new_prompt = tuning_bot.process(prompt, feedback)
        print('----------------------------------------------------')
        print()
        print(new_prompt.prompt)
        prompt = new_prompt.prompt
        print()

    Recorder.stop_recording(recording_name='system_prompt')
    Recorder.to_html_file(recording_name='system_prompt')

    prompt_file = input('Do you want to create a Prompt File y/n?')

    if prompt_file.strip().lower() == 'y':
        python_bot = DandyPythonPromptBot()
        python_bot.process(prompt)
