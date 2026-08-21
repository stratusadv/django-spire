# AI Usage & Interaction System

## Purpose

This app provides the system for tracking all AI interactions throughout a Django project.

## Installation

Simply add the ai application to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'django_spire.ai',
    ...
]
```

!!! warning

    A properly configured [Dandy](https://dandy.stratusadv.com/){:target="_blank"} install is required — Spire uses the Dandy LLM/recorder libraries under the hood.

## Usage

Given the probabilistic nature of AI, every interaction — especially ones involving users — should be tracked.

Below we make a simple interaction with the LLM and have the ai app track it:

```python
from dandy import Bot
from dandy.intel import BaseIntel

from django_spire.ai.decorators import log_ai_interaction_from_recorder


class HorseIntel(BaseIntel):
    first_name: str
    breed: str
    color: str
    has_cone_taped_to_head: bool


@log_ai_interaction_from_recorder(actor='Anonymous User')
def generate_horse_intel(user_input: str) -> HorseIntel:
    bot = Bot()
    return bot.llm.prompt_to_intel(
        prompt=user_input,
        intel_class=HorseIntel,
    )


horse_intel = generate_horse_intel('Make me a magical horse that grants wishes!')
```

The decorator records the interaction (module, callable, user or actor) and the full Dandy recorder trace. Pass `user=` when the acting user is known — the chat and SMS pipelines do this automatically:

```python
@log_ai_interaction_from_recorder(user=request.user)
def my_ai_work(request, user_input: str) -> None:
    ...
```

!!! warning

    The `log_ai_interaction_from_recorder` decorator is designed to be used with the Dandy intelligence library and will not track other LLM libraries properly.

## Admin

You can view AI interactions and daily usage in the Django admin under the `django_spire_ai` app.
