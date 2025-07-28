import django

from django_spire.ai.prompt.tuning.bots import PromptTuningBot

django.setup()

from dandy.recorder import Recorder

from django_spire.ai.prompt.bots import DandyPythonPromptBot
from django_spire.ai.prompt.system import bots

if __name__ == '__main__':
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
            PromptTuningBot()
            .process(prompt, feedback)
        )
        print('----------------------------------------------------')
        print()
        print(new_prompt.system_prompt)
        prompt = new_prompt.system_prompt
        print()

    Recorder.stop_recording(recording_name='system_prompt')
    Recorder.to_html_file(recording_name='system_prompt')
    DandyPythonPromptBot().process(prompt)
