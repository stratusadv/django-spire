from typing import Type

from dandy.llm import BaseLlmBot, Prompt
from dandy.recorder import Recorder

from django_spire.ai.prompt.bots import DandyPythonPromptBot
from django_spire.ai.prompt.tuning.bots import SimplePromptTuningBot


def bot_tuning_cli(bot: Type[BaseLlmBot], **bot_parmas):
    Recorder.start_recording(recording_name='prompt_tuning')

    tuned_prompt = bot.instructions_prompt
    print(tuned_prompt)
    bot_tuning = bot.process(**bot_parmas)
    print(bot_tuning)

    print('----------------------------------------------------')

    while True:
        print("\nEnter your feedback (or type 'stop' to finish):")
        feedback = input()

        if feedback == "stop":
            break

        print('Attempting to tune prompt.....')

        new_prompt = (
            SimplePromptTuningBot()
            .process(tuned_prompt, feedback)
        )

        print('----------------------NEW PROMPT START------------------------------')
        print()
        print(new_prompt.prompt)
        print()
        print('----------------------NEW PROMPT END------------------------------')
        print()
        print('----------------------BOT TUNING START------------------------------')
        bot.instructions_prompt = Prompt().text(new_prompt.prompt)
        bot_tuning = bot.process(**bot_parmas)
        print(bot_tuning)
        print('----------------------BOT TUNING END------------------------------')

        keep = input('Do you want to keep the changes y/n?')
        if keep.strip().lower() == 'y':
            tuned_prompt = new_prompt.prompt

    Recorder.stop_recording(recording_name='prompt_tuning')
    Recorder.to_html_file(recording_name='prompt_tuning')

    output_prompt = input('Do you want to output the final prompt y/n?')
    if output_prompt.strip().lower() == 'y':
        DandyPythonPromptBot().process(tuned_prompt)
