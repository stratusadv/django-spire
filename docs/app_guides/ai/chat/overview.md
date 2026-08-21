# AI Chat Assistant

## Purpose

This app provides an easy way to give end users a chat to interface with your project.

## Installation

Add the ai applications to your `INSTALLED_APPS`:

```python title="settings.py"
INSTALLED_APPS = [
    ...
    'django_spire.ai',
    'django_spire.ai.chat',
    ...
]
```

Then point the chat settings at your router class:

```python title="settings.py"
# which chat router handles messages by default
DJANGO_SPIRE_AI_DEFAULT_CHAT_ROUTER = 'SPIRE'

# name -> module path mapping of available routers
DJANGO_SPIRE_AI_CHAT_ROUTERS = {
    'SPIRE': 'example.ai.chat.router.ExampleChatRouter',
}

# the persona name used in the UI
DJANGO_SPIRE_AI_PERSONA_NAME = 'AI Assistant'
```

URLs are auto-discovered — make sure your project includes the Spire URL conf:

```python title="urls.py"
from django_spire.shortcuts import django_spire_urls

urlpatterns = [
    ...
]

urlpatterns += django_spire_urls()
```

!!! warning

    A properly configured [Dandy](https://dandy.stratusadv.com/){:target="_blank"} install is required.

## Usage

Chat messages are processed by a **chat router** — a subclass of `BaseChatRouter` whose `workflow()` method is the single place where user input is handled:

```python title="apps/ai/chat/router.py"
from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Bot

from django_spire.ai.chat.message_intel import BaseMessageIntel, DefaultMessageIntel
from django_spire.ai.chat.router import BaseChatRouter
from example.ai.chat.intelligence.message_intels import ClownMessageIntel

if TYPE_CHECKING:
    from dandy.llm.request.message import MessageHistory
    from django.core.handlers.wsgi import WSGIRequest


class ExampleChatRouter(BaseChatRouter):
    def workflow(
        self, request: WSGIRequest, user_input: str, message_history: MessageHistory | None = None
    ) -> BaseMessageIntel:
        bot = Bot()

        if 'clown' in user_input.lower():
            return bot.llm.prompt_to_intel(
                prompt=user_input,
                intel_class=ClownMessageIntel,
                message_history=message_history,
            )

        return DefaultMessageIntel(text='Sorry, I could not find any information on that.')
```

`workflow()` must return an instance of `BaseMessageIntel`. It is wrapped automatically with Dandy recorder logging and AI interaction tracking, and a missing/invalid result falls back to a default apology message.

### Message Intels

Messages are Dandy `BaseIntel` subclasses (pydantic models) that know how to render themselves:

```python title="apps/ai/chat/intelligence/message_intels.py"
from django_spire.ai.chat.message_intel import BaseMessageIntel


class ClownMessageIntel(BaseMessageIntel):
    _template = 'ai/chat/message/clown_message.html'
    clown_name: str

    def render_to_str(self) -> str:
        return self.render_template_to_str()
```

Set `_template` to a template that receives the intel's fields as context, and implement `render_to_str()` (or use `render_template_to_str()` when the template covers everything).

### Intent Routing

To dispatch specific intents to different routers (for example, knowledge-base lookups), declare them in settings:

```python
DJANGO_SPIRE_AI_INTENT_CHAT_ROUTERS = {
    'KNOWLEDGE_SEARCH': {
        'INTENT_DESCRIPTION': 'The user is asking about information, help or support that could be found in knowledge base.',
        'REQUIRED_PERMISSION': 'django_spire_knowledge.view_collection',
        'CHAT_ROUTER': 'django_spire.knowledge.intelligence.router.KnowledgeSearchRouter',
    },
}
```

The default `SpireChatRouter` already builds an intent decoder from these entries and falls back to your default workflow when no intent matches.

Once this is set up, simply add the chat card to your templates:

```html
{ % include 'django_spire/ai/chat/card/chat_card.html' % }
```

!!! tip

    Since this application uses a center point to process messages, make sure to fully utilize Dandy. This lets you route people from a central point to different areas of your application.
