# SMS Conversation

## Purpose

This app gives end users an SMS conversation to interface with your project — messages are routed through the same AI chat pipeline as the web chat.

## Installation

Add the applications to your `INSTALLED_APPS`:

```python title="settings.py"
INSTALLED_APPS = [
    ...
    'django_spire.ai',
    'django_spire.ai.sms',
    'django_spire.auth.sms',
    ...
]
```

URLs are auto-discovered — make sure your project includes the Spire URL conf:

```python title="urls.py"
from django_spire.shortcuts import django_spire_urls

urlpatterns += django_spire_urls()
```

The SMS webhook is mounted at `django_spire/ai/sms/webhook/` (route name `django_spire:ai:sms:webhook`).

!!! warning

    A properly configured [Dandy](https://dandy.stratusadv.com/){:target="_blank"} install is required.

## Environment Variables

Twilio credentials must be available in your environment and settings:

```python
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
```

Optional: cap the accepted inbound message length (default 1000 characters):

```python
DJANGO_SPIRE_AI_SMS_BODY_LENGTH_MAX = 1000
```

## Usage

Inbound Twilio deliveries hit `webhook_view`, which:

1. validates the sender against a verified `AuthSms` record (unregistered numbers are rejected)
2. guards against duplicate deliveries by Twilio message sid
3. enforces per-user throttling
4. manages the **session lock** — if the session is locked, the user must text back the unlock code generated in the app before chatting; the first valid code unlocks the conversation
5. passes the message to the framework's `sms_conversation_workflow`

The workflow runs the message through the [chat router](../chat/overview.md), then `SmsConversationBot` re-prompts the result into a concise, plain-text `SmsIntel` reply suitable for SMS. To customise what the SMS conversation does, point `DJANGO_SPIRE_AI_CHAT_ROUTERS` at your own router — both the web chat and the SMS conversation share it.

Point your Twilio number's webhook at:

```
https://yourproject.com/django_spire/ai/sms/webhook/
```

with a failure webhook at `django_spire/ai/sms/webhook/failed/` if you want an acknowledgement for failed deliveries.

!!! tip

    Since this application uses a center point to process messages, make sure to fully utilize Dandy. This lets you route people from a central point to different areas of your application.
