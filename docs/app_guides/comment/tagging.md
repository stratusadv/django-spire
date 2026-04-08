# Comment Tagging

> **Purpose:** Allow users to @mention other users in comments, automatically scraping tagged usernames from comment text and making the user list available to the tagging widget.

---

## Why Tagging?

Comments often need to pull specific people into a conversation. **The Comment Tagging system** provides:

- Automatic username scraping from comment text using `@username` syntax
- A utility to resolve tagged usernames to `User` objects
- A queryset helper to find users with access to a given model
- A `TaggingWidget` for rendering an autocomplete mention interface

---

## Core Concepts

### `@mention` Syntax

Tags are written inline in comment text as `@username`. The `Comment` model scrapes these automatically.

```python
comment.information = 'Hey @john_doe can you review this?'

comment.scrape_username_list()
# ['john_doe']

comment.find_user_list()
# <QuerySet [<User: john_doe>]>
```

### `scrape_username_list()`

Parses the comment's `information` field and returns a list of raw usernames (without the `@` prefix).

```python
comment.scrape_username_list() -> list[str]
```

### `find_user_list()`

Resolves the scraped usernames to a `User` queryset.

```python
comment.find_user_list() -> QuerySet[User]
```

---

## Main Operations

### Finding Taggable Users for an Object

Use `find_user_list_from_content_type` to get all users who have `view` permission on a given model — these are the candidates available in the tagging autocomplete.

```python
from django_spire.comment.utils import find_user_list_from_content_type

user_list = find_user_list_from_content_type(
    app_label='blog',
    model_name='blogpost',
)
```

This returns all users belonging to a group that has the `view_<model_name>` permission for the given content type.

### Generating Autocomplete Data for the Widget

Convert the user queryset to the JSON structure the `TaggingWidget` expects:

```python
from django_spire.comment.utils import generate_comment_user_list_data

user_list_data = generate_comment_user_list_data(user_list)
# [{'full_name': 'John_Doe', 'id': 1}, ...]
```

Names are returned with spaces replaced by underscores to match the `@mention` format.

### Using the Tagging Template Tag

The `user_list_from_content_type` template tag retrieves taggable users directly in a template:

```html
--8<-- "docs/app_guides/comment/templates/tagging_template_tag.html"
```

The result can then be passed to the comment form or widget.
