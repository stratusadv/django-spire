# AI Chat Assistant

## Purpose

This app provides an easy way to create a chat for end users to interface with the project.

## Installation

Simple add the ai application to your `INSTALLED_APPS` and the workflow class with module name to your settings:

```python title="settings.py"
INSTALLED_APPS = [
    ...
    'django_spire.ai',
    'django_spire.ai.chat',
    ...
]

# this is the class and module that will handle the chat interactions
AI_CHAT_WORKFLOW_CLASS = 'example.ai.chat.intelligence.chat_workflow.ChatWorkflow'
```

You also need to add django spire to your projects `urls.py`:

```python title="urls.py"
from django.urls import path, include

urlpatterns = [
    path('django_spire/', include('django_spire.urls', namespace='django_spire')),
]
```

!!! warning

    Properly configure Dandy install is required for more information see the [documentation](https://dandy.stratusadv.com/){:target="_blank"}.

## Usage

Your AI chat will need a workflow class that will be the place that all messages are sent to be processed.

The function you use will need to take 3 arguments:

- `request` - the request object: `django.core.handlers.wsgiWSGIRequest`
- `user_input` - the message from the user: `str`
- `message_history` - the message history of the chat: `dandy.llm.MessageHistory`

```python title="apps/ai/chat/intelligence/chat_workflow.py"
--8<-- "test_project/apps/ai/chat/intelligence/chat_workflow.py"
```

Once this is setup you can simply add the chat card to your templates:

```html
{ % include 'django_spire/ai/chat/card/chat_card.html' % }
```

!!! tip

    Since this application uses a center point to process messages make sure to fully utilize dandy.
    This will allow you to direct people from a central point to different areas of information.