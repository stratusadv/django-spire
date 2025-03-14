# Changelog

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

