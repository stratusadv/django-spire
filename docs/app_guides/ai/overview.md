# AI Usage & Interaction System

## Purpose

This app provides the system for tracking Dandy AI interactions throughout a django project.

## Installation

Simple add the ai application to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'django_spire.ai',
    ...
]
```

!!! warning

    Properly configure Dandy install is required for more information see the [documentation](https://dandy.stratusadv.com/){:target="_blank"}.

## Usage

When it comes to the probabilistic nature of AI we should track all interactions especially ones involving the users.

Below we are going to make a simple interaction with our llm bot and have the ai app track it.

```python
from dandy.intel import BaseIntel
from dandy.llm import LlmBot
from django_spire.ai.decorators import log_ai_interaction_from_recorder


class HorseIntel(BaseIntel):
    first_name: str
    breed: str
    color: str
    has_cone_taped_to_head: bool


@log_ai_interaction_from_recorder(actor='Anonymous User')
def generate_horse_intel(user_input: str) -> HorseIntel:
    return LlmBot.process(
        prompt=user_input,
        intel_class=HorseIntel,
    )


horse_intel = generate_horse_intel('Make me a magical horse that grants wishes!')
```

!!! warning

    the `log_ai_interaction_from_recorder` decorator is designed to be used with the Dandy intelligence library and will not work properly tracking other libraries.

## Admin

You can now view the ai interactions in the admin panel under the `Spire Ai` section.