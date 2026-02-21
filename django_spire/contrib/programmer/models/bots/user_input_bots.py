from __future__ import annotations

from dandy import Bot, Prompt

from django_spire.contrib.programmer.models.intel import intel


class ModelUserInputEnrichmentPrompt(Bot):
    role = 'Expert in understanding and explaining in simple terms.'
    task = 'Enrich the users input to provide more context for a Junior Developer to understand.'
    guidelines = (
        Prompt()
        .list([
            'The user is making a request to configure a django model file.',
            'Identify all models the user has mentioned and describe what they would like accomplished.',
            'Have one enriched model input for each model mentioned.',
            'Description on each enriched model is a list of tasks the user has requested.',
            'STAY AS ACCURATE AS POSSIBLE TO THE USER REQUEST. DO NOT MAKE ANYTHING UP.',
        ])
    )
    intel_class = intel.EnrichedModelUserInput
