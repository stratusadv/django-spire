# Comments

> **Purpose:** Attach threaded comment functionality to any model with a single mixin, providing full CRUD, reply support, and a drop-in template card — without building comment infrastructure from scratch.

---

## Why Comments?

User-generated discussion belongs close to the content it references. **The Comment system** provides:

- A generic `Comment` model that attaches to any model via Django's content types framework
- A `CommentModelMixin` that adds comment support to any model in one line
- Threaded replies via a self-referencing parent relationship
- Full CRUD through built-in views and a ready-made template card
- Edit tracking via `is_edited`

---

## Quick Start

### 1. Add the App

```python
INSTALLED_APPS = [
    ...
    'django_spire.comment',
]
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Add the Mixin to Your Model

```python
from django_spire.comment.mixins import CommentModelMixin

class BlogPost(CommentModelMixin):
    title = models.CharField(max_length=255)
    ...
```

### 4. Include the Template Card

Add the comment list card to your detail page template, passing the model instance as `obj`:

```html
<div class="col-12 col-xl-6">
    { include 'django_spire/comment/card/comment_list_card.html' with obj=blog_post }
</div>
```

That's it — the card handles rendering, creation, editing, and deletion.

---

## Core Concepts

### The `Comment` Model

Stores the comment text, author, timestamps, edit status, and a link to any model instance via Django's `ContentType` framework.

```python
from django_spire.comment.models import Comment
```

Key fields:

| Field | Description |
|---|---|
| `user` | The author (`User` FK) |
| `information` | The comment text |
| `content_type` / `object_id` | Generic FK linking the comment to its parent object |
| `parent` | Self-referencing FK for threaded replies (`null` for top-level comments) |
| `created_datetime` | Set automatically on creation |
| `is_edited` | Set to `True` when `update()` is called |
| `is_active` / `is_deleted` | Soft delete fields from `HistoryModelMixin` |

Comments are ordered by `-created_datetime` by default.

### The `CommentModelMixin`

Add this to any model to enable comments. It attaches a `GenericRelation` and provides the `add_comment()` helper.

```python
from django_spire.comment.mixins import CommentModelMixin
```

Adding the mixin gives your model:

- `obj.comments` — the `GenericRelation` queryset to all attached `Comment` records
- `obj.add_comment(user, information, parent=None)` — create a comment on this object

### The `CommentQuerySet`

Custom queryset available on `Comment.objects`.

| Method | Description |
|---|---|
| `active()` | Exclude soft-deleted comments |
| `top_level()` | Only return comments with no parent (exclude replies) |
| `prefetch_user()` | Prefetch the `user` relation |
| `prefetch_parent()` | Prefetch the `parent` relation |
| `prefetch_replies()` | Prefetch the `children` (reply) relation |

---

## Main Operations

### Adding a Comment to an Object

Use `add_comment()` on the mixin rather than creating `Comment` objects directly:

```python
blog_post = BlogPost.objects.get(pk=1)

blog_post.add_comment(
    user=request.user,
    information='Great write-up!',
)
```

### Adding a Reply

Pass a parent `Comment` or its `pk` to create a threaded reply:

```python
parent_comment = Comment.objects.get(pk=1)

blog_post.add_comment(
    user=request.user,
    information='Agreed — especially the second point.',
    parent=parent_comment,
)
```

### Querying Comments for an Object

```python
from django_spire.comment.models import Comment

# All active top-level comments for an object, with replies prefetched
comments = (
    Comment.objects
    .filter(content_type__model='blogpost', object_id=blog_post.pk)
    .active()
    .top_level()
    .prefetch_replies()
    .prefetch_user()
)
```

### Updating a Comment

```python
comment = Comment.objects.get(pk=1)
comment.update('Updated comment text.')
# Sets is_edited = True and saves
```

### Accessing Replies

```python
comment = Comment.objects.prefetch_related('children').get(pk=1)

for reply in comment.children.active():
    print(reply.information)
```

---

## Built-in URLs

The comment app registers its own URLs automatically. The available routes are:

| View | URL Pattern | Name |
|---|---|---|
| Comment form content (modal) | `comment/<comment_pk>/<obj_pk>/<app_label>/<model_name>/form/content/` | `django_spire:comment:form_content` |
| Comment form submit | `comment/<comment_pk>/<obj_pk>/<app_label>/<model_name>/form/` | `django_spire:comment:form` |
| Comment delete form (modal) | `comment/<comment_pk>/<obj_pk>/<app_label>/<model_name>/delete/form/` | `django_spire:comment:delete_form` |

Pass `comment_pk=0` to the form URLs when creating a new comment.
