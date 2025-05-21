# SMS Notification Guide

### 👀 Overview 
SMS Notifications in Django Spire are reliant on [Twilio's REST API](https://www.twilio.com/docs/messaging/api "Twilio SMS API Guide").

### 🎚️ Throttling and Batch Sizes
SMS notifications are processed in batches of 100 message segments and are intended to be processed in 5-minute intervals. This is because Twilio's SMS API has a limit of one message per second (for basic accounts),
and has a queue limit of 36,000 segments. ([see Twilio's documentation](https://www.twilio.com/docs/glossary/what-sms-character-limit "Twilio SMS Segments")).

See [Twilio's rate limits](https://help.twilio.com/articles/223183648-Sending-and-Receiving-Limitations-on-Calls-and-SMS-Messages "Twilio Rate Limits") for more details.

### 📱 Twilio Credentials
Twilio's credentials must be provided in the `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` environment variables. Additionally, the `TWILIO_SMS_BATCH_SIZE` environment variable must be set to the number of SMS messages to send per batch.
We recommend 100, as this is the maximum number of messages that can be sent per batch, but this can be changed as needed.

### Examples to come
