# Changelog

## v0.23.9

### Changes

- Better flexibility and support for card styles/classes

## v0.23.8

### Changes

- Change testing framework from unittest to pytest
- Improve typing, ruff adherence, code consistency
- CSS fixes

## v0.23.7

### Changes

- Update the progress tracker to use polling

## v0.23.6

### Changes

- Update the progress tracker to use POST

## v0.23.5

### Changes

- Update the progress tracker and handle futures
- Change height of skeleton loading element
- Update infinite scrolling default batch size to 50

## v0.23.4

### Changes

- Added a boolean flag to the process session filter to retrieve data from the body

## v0.23.3

### Changes

- Cleaned up the knowledge to ai chat work flow and improved the message result.

## v0.23.2

### Changes

- Handle query parameters more gracefully in infinite scroll

## v0.23.1

### Fixes

- Fix queryest session filtering when a session resumes.
- Add a session controller condition so that, when a session is expired, it returns an unfiltered queryest.

## v0.23.0

### Breaking

- infinite_scrolling_view and its subsequent templates have been refactored

### Changes

- The ability to capture form errors and pass them to context data

### Features

- Infinite loading cards, containers, pages and tables
- Tables
- Lazy-loaded tabs

## v0.22.4

### Changes

- Knowledge base editor CSS theme support.

## v0.22.3

### Fixes

- Fixed knowledge base navigation missing child collections bug.

## v0.22.2

### Fixes
- Fixed knowledge base file conversion bug.

## v0.22.1

### Fixes

- Fixed migration file issues with `django_spire_core` and sub-app `tag` model.

## v0.22.0

### Features

- Tagging system functionality is refactored and enhanced to include scoring and weighting.
- Knowledge now uses multiple methods of tagging for interactions with AI.
- AI Chat now searches knowledge almost 10x faster and more accurately.

## v0.21.1

### Fixes

- Fixed CSS issues related to chat/knowledge_base/full_page

## v0.21.0

### Breaking

**Settings Renamed**
- All `AI_*` settings renamed to `DJANGO_SPIRE_AI_*` for consistency
- `AI_PERSONA_NAME` → `DJANGO_SPIRE_AI_PERSONA_NAME`

**Example:**
```python
# Before
AI_PERSONA_NAME = 'Assistant'
AI_CHAT_DEFAULT_CALLABLE = 'path.to.workflow'

# After
DJANGO_SPIRE_AI_PERSONA_NAME = 'Assistant'
```

**Settings Removed**
- `AI_CHAT_CALLABLE`
- `AI_CHAT_DEFAULT_CALLABLE`
- `AI_SMS_CONVERSATION_DEFAULT_CALLABLE`
- `ORGANIZATION_NAME`
- `ORGANIZATION_DESCRIPTION`

**BaseMessageIntel Method Renames**
- `render_to_str()` → `render_template_to_str()`
- `content_to_str()` → `render_to_str()`

### Features

**Router Architecture**
- New `BaseChatRouter` abstract base class for extensible AI chat implementations
- New `SpireChatRouter` default router

**Intent-Based Routing**
- Automatic query routing to specialized routers based on user intent
- Permission-based access control for intent routes
- Automatic fallback to default chat when no intent matches

**New Settings**

`DJANGO_SPIRE_AI_CHAT_ROUTERS` - Map router keys to class paths:
```python
DJANGO_SPIRE_AI_CHAT_ROUTERS = {
    'SPIRE': 'django_spire.ai.chat.router.SpireChatRouter',
}
```

`DJANGO_SPIRE_AI_INTENT_CHAT_ROUTERS` - Configure intent-based routing:
```python
DJANGO_SPIRE_AI_INTENT_CHAT_ROUTERS = {
    'KNOWLEDGE_SEARCH': {
        'INTENT_DESCRIPTION': 'User asking about knowledge base',
        'REQUIRED_PERMISSION': 'app.view_knowledge',
        'CHAT_ROUTER': 'app.routers.KnowledgeRouter',
    },
}
```

`DJANGO_SPIRE_AI_DEFAULT_CHAT_ROUTER` - Specify default router key (defaults to 'SPIRE' if not set)

## v0.20.4

### Changes

- Dispatch message upon theme change

## v0.20.3

### Changes

- Theme expansion for more customization

## v0.20.2

### Changes

- Added optional file attachments to email notifications.

## v0.20.1

### Changes

- Added a new setting `AI_CHAT_CALLABLE` that allows you to completely override the django spire chat workflow.

## v0.20.0

### Feature

- New mixin `django_spire.core.tags.mixin` this allows your to properly store and retrieve tag sequences on a model.
- Knowledge app ai workflow complete overhaul.

## v0.19.5

### Changes

- Remove Dracula, Oceanic-Next and Synthwave theme

## v0.19.4

### Fixes

- Fix spire_startapp command to create proper app labels
- Add a templatetag to allow navigation tracking

## v0.19.3

### Fixes

- Update theme CSS on dark mode

## v0.19.2

### Changes

- Truncate chat name based on message

### Fixes

- Fix chat/knowledge issue that gave a 500 status code
- Fix tool typing issues

## v0.19.1

### Changes

- Fix minor CSS issues in AI Chat
- Fix spire_startapp to include ".html" extension in views

## v0.19.0

### Breaking

- The `djangospire.knowledge` app and it's sub apps have been refactored along with its functionality.
- The `djangospire.ai.chat` app has been refactored.
- `settings.AI_CHAT_WORKFLOW_NAME` changed to `settings.AI_PERSONA_NAME`
- `settings.AI_CHAT_WORKFLOW_CLASS` changed to `settings.AI_CHAT_DEFAULT_CALLABLE`
- `settings.AI_SMS_CONVERSATION_WORKFLOW_CLASS` changed to `settings.AI_SMS_CONVERSATION_DEFAULT_CALLABLE`
- `settings.ORGANIZATION_NAME` has been removed, refer to `django_spire.ai.context`
- `settings.ORGANIZATION_DESCRIPTION` has been removed, refer to `django_spire.ai.context`

### Changes

- `settings.AI_CHAT_DEFAULT_CALLABLE` is no longer mandatory.
- `settings.AI_SMS_CONVERSATION_DEFAULT_CALLABLE` is no longer mandatory.

### Feature

- New app `django_spire.ai.context` has been added to create organizational context for the all AI features.
- Template `django_spire/page/full_page.html` has two new blocks for creating additional navigation.
  - Block `full_page_sub_navigation` automatically displays when it has content on the left/start and pushes `full_page_content`.
    - Also see `full_page_sub_navigation_title` and `full_page_sub_navigation_buttons`.
  - Block `full_page_info_navigation` works similar but does not push content and is on the right/end.
    - Also see `full_page_info_navigation_title` and `full_page_info_navigation_buttons`.
- Added a button to the profile in the top navigation that allows super users to quickly get to the theme dashboard.
- The theme app is much more complete and shows all theming on layer 1 and 2 for better design.
- Created primary dark outlined button.

### Fixes

- Updated `django_spire.ai.chat` and `django_spire.knowledge` to use new sub nav.
- Fixed css for `text-app-success` and all variants.
- Primary button outlined fixed from dark primary colouring to primary.


## v0.18.3

### Fixes
- Fixed duplicate content during Knowledge Base conversion process.


## v0.18.2

### Fixes
- Fixed incorrect ordering for app notification list and dropdown.
- Fixed bad dandy call in base seeder.


## v0.18.1

### Fixes

- Add missing migration file for Knowledge Base.


## v0.18.0

### Features

- Knowledge Base editor refactored to EditorJS.
  - Full ordered and unordered list support.
  - Link support.
  - Checkbox support.
  - Text styling support.
  - H1-H6 Heading support.
  - Paragraph support.
  - Editor UI / UX improvements.

### Changes

- Knowledge Base file conversion refactored to support EditorJS refactor.
  - Paragraph, heading, lists, and checkbox support 


## v0.17.11

### Fixes
- Update `Dandy` requirement to v1.2.1

## v0.17.10

### Fixes
- Knowledge base file page UI bug fix
- Knowledge base side navigation UX improvement


## v0.17.9

### Changes
- Loosen robit requirement


## v0.17.8

### Changes
- Removed hard-coded colours from v0.17.7


## v0.17.7

### Changes

- Replaced right click context menus with options button in knowledge base and improved look of options menu items 
- Removed collections detail page from knowledge base
- Change knowledge base side navigation to share page space with main content, rather than slide over top (kept overlay behaviour for mobile screens)
- Restricted knowledge item reordering to users with change_collection permission
- Added support for icons in core dropdown menus


## v0.17.6

### Changes

- Update dandy to v1.1.4


## v0.17.5

### Changes

- Add an experimental progress bar to add events to dandy


## v0.17.4

### Fixes

- Update dandy to v1.1.3


## v0.17.3

### Changes
- Create `ChatBot` for AI Chat app.

### Fixes
- Fixed Knowledge Base AI crash bug fix.


## v0.17.2

### Changes
- Dandy v1.1.2

### Fixes
- System prompting bot and futures fix. 


## v0.17.1

### Changes
- Package .template files for the spire_startapp command


## v0.17.0

### Changes
- Added profiling middleware / django_debug_toolbar integration using the profiling middleware
- Modified the spire_startapp to use a wizard and be more flexible


## v0.16.13

### Breaking 
- Dandy v1 now a requirement. Review Dandy documentation and review bot setup. 
- Review Dandy Settings file. 


## v0.16.12

### Breaking
- Modified default file storage to use Digital Ocean Spaces.
- Added mandatory BASE_FOLDER_NAME to settings to allow for Digital Ocean Spaces organization.
- Knowledge Base must use Digital Ocean Spaces for file storage / retrieval. 

### Changes
- Added optional class variable `app_name` to `FileUploader` class. Recommended for organization purposes.
- Updated Knowledge Base file upload and conversion to use Digital Ocean Spaces.


## v0.16.11

### Breaking
- Removed `app_bootstrap_icon` from context processors.
- Removed remaining hard-coded colours. Check theme page for any issues.

### Changes
- Updated Help Desk permission to new AuthController structure.
- Login page 'Username' label changed to 'Email Address'.
- Unified dropdown item styling.
- Improvement dropdown item styling.
- Removed all remaining hard-coded colours.
- Knowledge Base UI improvements.

### Fixes
- Knowledge Base access bug fix.
- Fixed transparent dropdown items.


## v0.16.10

### Changes
- Updated modal to close on mousedown outside.
- Fine tune spire start app command to populate correct naming.


## v0.16.9

### Changes
- Knowledge Base UI improvements.

## v0.16.8

### Changes
- Override icon on fields for full Chromium theme support.
- Knowledge Base UI improvements.


## v0.16.7

### Changes
- Collection parent assignment control.

### Fixes
- Fixed Knowledge Base Collection special permission missing collections bug.


## v0.16.6

### Changes
- Added custom group permissions to Knowledge Base Collections.
- Added Knowledge Base Collection menu edit option. 

### Fixes
- Fixed skipped theme tests.


## v0.16.5

### Breaking
- Password change return url changed to 'home:page:home'

### Changes
- Added to_json template tag.
- Added top navigation icon blocks.
- Password change form UI improvements.
- Updated theme urls and views to best practice.

### Fixes
- Top navigation dropdown menu URL fixes.


## v0.16.4

### Changes
- Updated CSS styling on all dropdown.
- Added better padding to ellipsis dropdown menu.

### Fixes
- Fixed broken buttons on user dropdown menu in top navigation (This time in proper template :))

## v0.16.3

### Fixes
- Fixed broken buttons on user dropdown menu in top navigation.

## v0.16.2

### Changes
- Updated CSS theme variables to match changes made in v0.15.7

### Fixes
- Fixed AI Chat repeated response bug.


## v0.16.1

### Breaking
- Django Spire AI Settings have been moved into the Django Spire settings file.
- Organization Name and Description must be set in the django spire settings file in order for the AI Chat to work properly. 

### Changes
- Django Spire AI Chat workflow and SMS workflow created
- Knowledge Base AI Chat improvements
- AI Chat Quotations Error Handling
- AI Chat UI / UX Improvements


## v0.16.0

### Changes
- Added the ability to create and customize themes

## v0.15.11

### Changes
- Improved UI/UX for Group Detail Page

## v0.15.10

### Changes
- Improved system prompt bot to have a better prompt structure.
- Added System Prompt Testing Bot to easily test responses from bots.


## v0.15.9

### Changes
- Added Knowledge Base folder side navigation.


## v0.15.8

### Fixes
- Fixed group user form from breaking when names contained escape characters.

## v0.15.7

### Breaking
- Removed `app-layer-five` and default background css variable.
- CSS classes changed to reflect definition of layer-one, layer-two, etc. Please review the new app.css file and use the theme page for any issues.

### Changes
- Updated templates to reflect definitions of layer-one, layer-two, etc.
- Added alternate layer classes.
- Added side navigation, top navigation and footer background, text, link and link hover CSS variables.
- Added top navigation height as css variable.
- Modified AI Chat to use top navigation height.


## v0.15.6

### Changes
- Added inactive function in History Queryset


## v0.15.5

### Features
- Added default 'All Users' group that applies to all users that are created.


## v0.15.4

### Changes
- Added Knowledge Base Admin Files

### Fixes
- Knowledge Base Collection Deletion Bug Fix.


## v0.15.3

### Changes
- Added fonts to package data bundling


## v0.15.2

### Changes
- Added override block to modal column sizes


## v0.15.1

### Changes
- Added AI Chat Home Page

### Fix
- Some Knowledge Base Permissions

## v0.15.0

### Breaking

- The `permissions_required` decorator now takes position arguments instead of an optional tuple.
- Templates in the 'django_spire/auth/user_account' directory have been moved to 'django_spire/auth/user'
- Templates in the 'django_spire/auth/permission' directory have been moved to 'django_spire/auth/group'
- The form views that were previously in 'django_spire/auth/user/page_views.py' have been moved to 'django_spire/auth/user/views/form_views.py'
- The form URLs that were previously in 'django_spire/auth/user/urls/page_urls.py' have been moved to 'django_spire/auth/user/urls/form_urls.py'
- The form views that were previously in 'django_spire/auth/group/page_views.py' have been moved to 'django_spire/auth/group/views/form_views.py'
- The form URLs that were previously in 'django_spire/auth/group/urls/page_urls.py' have been moved to 'django_spire/auth/group/urls/form_urls.py'
- Page view URLs for the 'AuthUser' and 'AuthGroup' now require the 'page' namespace

### Feature

- Knowledge Base Feature Release
  - CRUD for collection, entries and blocks.
  - Importing docx and markdown files.
  - Use the AI Chat to search the knowledge base.
  - Drag and drop ordering.
- `AuthController` has been added to control all the app permissions in an explicit way that follows django practices.

### Fix

- Fixed permission decorator to redirect to login.
- Fixed broken urls that were in the base templates for the 'AuthUser' and 'AuthGroup' apps.


## v0.14.8

### Changes
- Optimize modal column sizes for different screen sizes


## v0.14.7

### Changes
- Implemented a profiling middleware


## v0.14.6

### Changes
- Added Django Glue Fields and Example Theme Page.
- Changed hard-coded colours across system.
- Added hover colouring on all buttons.

### Breaking
- Potential broken CSS / colours. Review theme page for any issues. 


## v0.14.5

### Changes
- Added css variables for attribute title and tweaked css styling. 


## v0.14.4

### Changes
- Updated theme apps.py file to allow for url access. 


## v0.14.3

### Changes
- Updated `spire_startapp` template testing file structure.

## v0.14.2

## Change
- Moved default spire notification dropdown position to be at the top center of screen on mobile devices

## v0.14.1

## Breaking

- Activity templates moved from `django_spire/history` to `django_spire/activity`
- Renamed `activity_list_card.html` template to `list_card.html` (Import path is now `django_spire/card/list_card.html`)

### Fixes
- Fixed generic `poral_delete_form` raising error on page load. 

## v0.14.0

### Features
- Spire theme app to help view and style your application's theme!

### Change
- Default css text colors with root variables. 
- Spire start app command has improved naming and file structure. 


## v0.13.1

### Change
- Change default infinite scroll card title class and add optional card title class block


### Fixes
- Fix for type checking Base Constructor.


## v0.13.0

### Breaking

- `BaseService` has been removed from `django_spire.contrib.service`

### Features

- `django_spire.contrib.constructor` has been added as a way to extend our interfacing.
  - `BaseDjangoModelConstructor` can be used to develop structure interfacing with Django models.

### Changes

- `django_spire.contrib.constructor.BaseConstructor` replaces `django_spire.contrib.service.BaseService`
- `BaseDjangoModelService` now inherits from `django_spire.contrib.constructor.BaseDjangoModelConstructor`


## v0.12.7
### Change
- Service layer validation reads through MRO to allow dependent objects to re-use services.  


## v0.12.6
### Features
- spire_startapp management command that creates a new app with Spire's best practices. 
- Experimental Ai prompting command line features.


## v0.12.5

### Fixes
- Refactored HelpDesk `save_model_obj` calls.

## v0.12.4

### Changes
- `BaseDjangoModelService save_model_obj` changed to return a tuple of (obj, created).

### Breaking
- Previous save_model_obj calls must be refactored for new return tuple.


## v0.12.3

### Tools
- Phone number to international number formatter


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
