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

    def process(self, user_input: str) ->list[str]:
        # Ensure that we have the correct model files...

        start_time = tui.printer.start_task('Enriching User Input', 'enriching')
        enriched_prompt_intel = ModelUserInputEnrichmentPrompt().process(prompt=user_input)
        tui.printer.end_task(start_time, 'Prompt Enriched!')

        happy = False
        while not happy:
            # Set and find the correct model files.
            feedback = tui.get_user_input(f'Are these the correct model names? \n\n {enriched_prompt_intel.model_names_to_prompt()}')

            happy_user_intel = HappyUserBot().process(feedback)
            if happy_user_intel.is_happy:
                break

            start_time = tui.printer.start_task('Name all the models.', 'tuning')

            feedback_prompt = (
                Prompt()
                .text('The user is providing feedback on the model names. Leave the other fields unchanged.')
                .text(feedback)
            )

            enriched_prompt_intel = FeedBackBot().process(
                response=enriched_prompt_intel.to_prompt(),
                feedback=feedback_prompt,
                bot=ModelUserInputEnrichmentPrompt
            )
            tui.printer.end_task(start_time, 'Models Adjusted!')

        model_intels = []
        for enriched_data in enriched_prompt_intel.enriched_model_input:
            start_time = tui.printer.start_task(f'Locating {enriched_data.model_name}', 'locating')
            model_intel = ModelFinderBot().process(enriched_data.model_name)
            tui.printer.end_task(start_time, model_intel.path)
            model_intels.append(model_intel)

        happy = False
        while not happy:
            feedback = tui.get_user_input(f'Are these the correct model names? \n\n {enriched_prompt_intel.to_prompt()}')

            happy_user_intel = HappyUserBot().process(feedback)
            if happy_user_intel.is_happy:
                break

            start_time = tui.printer.start_task('Providing Feedback', 'tuning')

            enriched_prompt_intel = FeedBackBot().process(
                response=enriched_prompt_intel.to_prompt(),
                feedback=feedback,
                bot=ModelUserInputEnrichmentPrompt
            )
            tui.printer.end_task(start_time, 'Prompt Enriched!')

        changed_files = []

        # Move through each model file.
        for enriched_data in enriched_prompt_intel.enriched_model_input:
            enriched_user_input = enriched_data.to_prompt()

            # Find the model file.
            model_file = ModelFileFinderBot().process(user_input=enriched_data.model_name)

            actions = {
                'Model Fields': ModelFieldOrchestrationBot,
                'Model Methods': ModelFieldGeneralProgrammerBot,
                # 'New Model File': ModelProgrammerBot,
                # 'Review a model file': ModelProgrammerBot,
            }

            prompt = (
                Prompt()
                .heading('User Request')
                .text(enriched_user_input)
                .heading('Typical Order of Events')
                .ordered_list([
                    'Create the model file if it is empty',
                    'Model Fields',
                    'Model Methods',
                    'Review for best practices'
                ])
                .heading('Model File')
                .text(model_file)
            )

            action_bots = self.llm.decoder.prompt_to_values(
                prompt=prompt,
                keys_description='Actions a programmer takes on a django model file',
                keys_values=actions,
            )

            # Take actions on the model file
            for bot in action_bots:
                model_file = bot().process(user_input=enriched_user_input, model_file=model_file)

            changed_files.append(model_file)

        return changed_files