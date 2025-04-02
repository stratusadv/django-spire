# Changelog

## V0.2.0
### Feature
- Seeder refactored into Field Seeder and Model Seeder
- Specific Seeder for Django Models
- Class based usage for Model Seeding.

### Breaking
- ModelSeeder has been refactored to DjangoModelSeeder  


## V0.1.37
### Feature
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
