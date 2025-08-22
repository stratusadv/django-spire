from django_spire.ai.prompt.tuning.bots import SimplePromptTuningBot
from dandy.recorder import Recorder

from django_spire.ai.prompt.bots import DandyPythonPromptBot
from django_spire.ai.prompt.system import bots

def create_system_prompt_cli():
    Recorder.start_recording(recording_name='system_prompt')

    user_story = input('Enter your user story: ')
    prompt = bots.SystemPromptBot.process(user_story)
    print(prompt)

    while True:
        print("\nEnter your feedback (or type 'stop' to finish):")
        feedback = input()

        if feedback == "stop":
            break

        print('Creating new prompt from feedback.....')
        new_prompt = (
            SimplePromptTuningBot()
            .process(prompt, feedback)
        )
        print('----------------------------------------------------')
        print()
        print(new_prompt.prompt)
        prompt = new_prompt.prompt
        print()

    Recorder.stop_recording(recording_name='system_prompt')
    Recorder.to_html_file(recording_name='system_prompt')

    prompt_file = input('Do you want to create a Prompt File y/n?')
    if prompt_file.strip().lower() == 'y':
        DandyPythonPromptBot().process(prompt)
