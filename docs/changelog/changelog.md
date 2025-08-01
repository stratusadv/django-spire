# Changelog

## v0.12.2

### Fixes
- Django Service bug fixed when striping "_id" to match field names. 



## v0.12.1

### Fixes
- Corrected Help Desk 'Add' Permissions


## v0.12.0
### Features
- Help Desk System Prototype with Basic Permissions
  - Full CRUD for tickets.
  - Email and app notifications to ADMINS when a ticket is created.
  - App notifications to 'delete' perm users when a ticket is created.

### Breaking
- Must include DEVELOPMENT_EMAIL in settings file that pulls from env.


## v0.11.0
## Features
- Session controller class to help manage session data with timeouts.
- Session controller js class and template tags to access session data within alpine js.
- Queryset app with session filtering tools

## Breaking
- Core filtering app no longer exists. Tool improved and transferred into contrib/queryset 


## v0.10.2
### Fixes
- Fixed App Notification Ordering
- Fixed Django Error when accessing the `App Notificaiton Dropdown` as an anonymous user.
- Added protection to 'SmsTemporaryMedia' view to prevent rendering non-existent media.
- Fixed Email Notification Url


## v0.10.1

### Feature
- Added PNG compression to SMS Temporary Media view.


## v0.10.0

### Changes
- Service changed to use generic typing and object reference.

### Breaking
- Service must take an obj with type annotations. 
- See the docs for other small changes. 


## v0.9.8

### Changes
- Improved SMS Notification Admin Panel


## v0.9.7

### Features
- Model class added to base service initialization


## v0.9.6

### Features
- Created filtering util functions.
- Created view glue accordion template.


## v0.9.5

### Fixes
- ``DjangoModelService`` can properly initialize from future refs to avoid type checking errors.
- Caching the service instance onto the target object to avoid unnecessary initialization.  
- Test for services moved into the test_project for a realistic environment.

### Breaking
- ``model_obj_validate_field_data`` refactored to ``validate_model_obj``
- ``model_obj_validate_field_data_and_save`` refactored to ``save_model_obj`` 

## v0.9.4

### Fixes
- Fixed incorrect external urls for `HelpDesk Notifications` and `SmsTemporaryMedia External Url`.

## v0.9.3

### Features
- Django Glue List Filtering System.
    - Filtering Tutorial Docs

### Changes
- Added `app-override.css` file to allow for easy overriding of Spire CSS classes.

## v0.9.2

### Features

- Added tool to  the `File` app for copying filed from one model to another.  

## v0.9.1

### Features

- Added content object querysets to all `Notification` queryset managers

## v0.9.0

### Features

- AI SMS Conversation App
  - Integration with Twilio SMS Webhook for Managing SMS Conversations
- Help Desk Prototype
  - Ticket List
  - Ticket Form
  - Notifications for Ticket Creation to Developers and Managers
- Added custom template_id, context_data, bcc and cc to `EmailNotification` model
- SMS Notifications now support MMS
  - Temporary Media added for developers to publicly expose media for MMS messages
- JSON Tree Input Widget for Admin Panel
- Service Layer Abstraction is now ready for use with `BaseService` and `BaseDjangoModelService`.
  - both located in the `django_spire.contrib.service`

### Fixes

- Fixed missing login required decorator on multiple views.

## v0.8.2

### Fixes

- Fixed missing login required decorator on multiple views.

### Features

- Added `App Notification` list view filtering to include priority.

## v0.8.1

### Fixes

- Fixed missing login required decorator on `app_notification_list_view`.

## v0.8.0

### Features

- Base service layer and descriptor to extend models.
- Default service for common functionality (saving an instance).


## v0.7.1

### Fixes

- Fixed incorrect testing database.
- Fixed incorrect import for `TWILIO_SMS_BATCH_SIZE`.

### Features

- Test Project now has `django-spire.notification` installed, with the ability to create and process them.
- Updated Documentation to include examples of notifications.

## v0.7.0

### Breaking

- Prior installations of `django-spire.notification` will be broken.
- Previous AI chat's and chat messages will not be compatible with the new chat system.

### Features

- App Notifications
- Email Notifications
  - Helper for SendGrid Email API
- SMS Notifications
  - Requires a Twilio Account and a phone number to be setup.
- AI Chat message rendering system.
- AI Chat Text to Speech and Speech to Text.

### Changes

- Moved `user` field to `Notification` model.
- Notification templates have been updated to be more consistent across projects.

## v0.6.1

### Fixes

- AI Chat UI and UX changes to make chat seem more natural. 

## v0.6.0

### Breaking

- Fixes for refactoring errors and import errors.

### Features

- Improved the `django_spire.ai.chat` application with more standard features and refactoring of naming.

### Changes

- Removed `testing` and `example` projects and converted everything into `test_project`.
- Adjusted `django_spire.contrib.seeding` to be more accurate and consistent.

## v0.5.*

### Breaking

- Fixes for refactoring errors and import errors.

## v0.5.0

### Breaking

- The word 'spire' has been replaced throughout the project with 'django_spire', this will break most existing code.
- Most of the project has been completely refactored, and all uses of this package will need to be reviewed.

## v0.4.1

### Changes

#### Django Model Seeder
- Custom methods to seed foreign keys to solve class variables initiation issues.
- In order custom method loops back on itself to keep seeding values.
- Django LLM Seeder processes to futures when the count is over 25.
- Field Override checks seeder class when calling methods.

## v0.4.0

### Features

- New app `django_spire.ai` that is used for tracking usage and debugging AI interactions inside your project.
- New app `django_spire.ai.chat` that is used for creating a chat for end users to interface with the project through AI.

## v0.3.4

### Features
 
- Field override added to model seeder. Chain fields together for re-usability.

## v0.3.3

### Changes

- Ordering django model seeder fields for consistent hashing. 
- Model seeding defaults to caching. 
- Remove emojis from documentation. 
- Custom datetime method for seeding aware date times.
- Seeding Foreign Keys requires the id value and the field name suffixed `_id`.

### Fixes

- Updated importing for all apps to follow a standard INSTALLED_APPS process.

## v0.3.0

### Breaking

- Seperated `django_spire.history` into `django_spire.history.activity` and `django_spire.history.viewed`

### Features

- New app called `django_spire.ai` that is used for tracking and debugging ai interactions inside your project.'
  - Check documentation for more details.
- New app called `django_spire.notification` that is used for sending notifications to users.
  - this app includes email and in application notifications.
  - Check documentation for more details.

### Changes

- Moved around documentation.

### Fixes

- Updated testing structure for the maintenance of Django Spire.

## V0.2.1

### Changes
- Field config object for model seeding

### Fixes
- Foreign key field translations removed because of overriding fields issue.


## V0.2.0

### Features

- Django seeding management command to create seeder classes for models.
- Caching model seed data values

### Changes

- Seeder refactored into Field Seeder and Model Seeder
- Specific Seeder for Django Models
- Class based usage for Model Seeding.


### Breaking

- ModelSeeder has been refactored to DjangoModelSeeder  


## V0.1.37

### Features

- Model Seeding with llm, faker, callable, static and custom methods!

### Breaking

- SeedingProcessor is no longer a thing. View the documentation to learn about Model Seeding and refactor your code.  



## V0.1.36

### Breaking

- Refactored to Django Glue v0.8.1 and Dandy v0.13.2. Check the repository change logs before upgrading.  
- Django Glue Changelog: https://django-glue.stratusadv.com/changelog/changelog/
- Dandy Changelog: https://dandy.stratusadv.com/changelog/changelog/


## V0.1.35

### Changes

- Allow the user to use `shared_payload` for searching, filtering, etc. and add a loading indicator to  `infinite_scroll_card.html`  

## V0.1.34

### Fixes

- Fix `infinite_scroll_card.html` to work on list pages; not just cards

## V0.1.33

### Fixes

- Fix `process_request_body` to accept a key `kwarg`

## V0.1.32

### Features

- Added seeding prompt function to prompt Model field on specific choices

## v0.1.30

### Changes

- Template tag file name to start with `spire_` to be more verbose for dependant projects `{% load spire_core_tags %}`
- Doc strings added to available functions. 

### Breaking 

- `core/templatetags/core_tags.py` has been refactored to `core/templatetags/spire_core_tags.py`
- `db/shortcuts.py` has been refactored to `core/shortcuts.py`

## v0.1.24

### Features
- added seeding prompts to assist with seeding django models.

### Fixes
- A lot of refactoring for the seeding app.

## v0.1.23

### Changes

- Refactored seeding.

## v0.1.22

### Fixes

- Correct import paths for Ai Seeding Bot.
