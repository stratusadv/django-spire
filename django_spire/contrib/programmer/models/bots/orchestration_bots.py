from dandy import Bot, Prompt
from dandy.cli.tui.tui import tui

from django_spire.contrib.programmer.models.bots.general_bots import HappyUserBot, FeedBackBot
from django_spire.contrib.programmer.models.bots.model_bots import ModelFieldGeneralProgrammerBot
from django_spire.contrib.programmer.models.bots.user_input_bots import ModelEnrichmentPrompt
from django_spire.contrib.programmer.models.intel import intel


class ModelOrchestrationBot(Bot):
    role = 'An expert at finding and orchestrating tasks that need to be completed.'
    task = 'Return actions in the correct order they need to be taken.'
    guidelines = (
        Prompt()
        .list([
            'A user will provide you with a request to perform actions on a django model.',
            'Break down that request into actions a programmer needs to take.',
            'Use the existing model file as context to help make a better decision.'
        ])
    )

    def process(self, user_input: str) ->intel.ModelsIntel:

        # Enrich the users prompt
        start_time = tui.printer.start_task('Enriching User Input', 'enriching')
        models_intel = ModelEnrichmentPrompt().process(prompt=user_input)
        tui.printer.end_task(start_time, 'Prompt Enriched!')

        happy = False
        while not happy:
            # Correct model files
            feedback = tui.get_user_input(f'Are these the correct model names? \n\n {models_intel.names_to_prompt()}')

            happy_user_intel = HappyUserBot().process(feedback)
            if happy_user_intel.is_happy:
                break

            start_time = tui.printer.start_task('Name all the models.', 'tuning')

            feedback_prompt = (
                Prompt()
                .text('The user is providing feedback on the model names. Leave the other fields unchanged.')
                .text(feedback)
            )

            models_intel = FeedBackBot().process(
                response=models_intel.to_prompt(),
                feedback=feedback_prompt,
                bot=ModelEnrichmentPrompt
            )
            tui.printer.end_task(start_time, 'Models Adjusted!')

        # Set the file and path to each model.
        for model_intel in models_intel.models:
            start_time = tui.printer.start_task(f'Locating {model_intel.name}', 'locating')
            model_intel.find()
            tui.printer.end_task(start_time, model_intel.path)

        # Confirm all the tasks the bot should take
        happy = False
        while not happy:
            feedback = tui.get_user_input(f'Are these the correct actions to take? \n\n {models_intel.to_prompt()}')

            happy_user_intel = HappyUserBot().process(feedback)
            if happy_user_intel.is_happy:
                break

            start_time = tui.printer.start_task('Providing Feedback', 'tuning')

            models_intel = FeedBackBot().process(
                response=models_intel.to_prompt(),
                feedback=feedback,
                bot=ModelEnrichmentPrompt
            )
            tui.printer.end_task(start_time, 'Prompt Enriched!')

        for model_intel in models_intel.models:
            actions = {
                'Model Fields': ModelFieldGeneralProgrammerBot,
                'Model Methods': ModelFieldGeneralProgrammerBot,
                # 'New Model File': ModelProgrammerBot,
                # 'Review a model file': ModelProgrammerBot,
            }

            prompt = (
                Prompt()
                .heading('User Request')
                .text(model_intel.to_prompt())
                .heading('Typical Order of Events')
                .ordered_list([
                    'Create the model file if it is empty',
                    'Model Fields',
                    'Model Methods',
                    'Review for best practices'
                ])
                .heading('Model File')
                .text(model_intel.file)
            )

            action_bots = self.llm.decoder.prompt_to_values(
                prompt=prompt,
                keys_description='Actions a programmer takes on a django model file',
                keys_values=actions,
            )

            # Take actions on the model file
            for bot in action_bots:
                model_file = bot().process(
                    prompt=models_intel.to_prompt(),
                    model_file=model_intel.file
                )

                model_intel.file = model_file.python_file

            self.file.write(
                file_path=model_intel.path,
                content=model_intel.file
            )

        return models_intel
