## Installation

Add `django_spire.comment` application to your `INSTALLED_APPS` to your settings:

```python title="settings.py"
INSTALLED_APPS = [
    ...
    'django_spire.comment',
    ...
]

```

## Enabling Comments for a Model

Comment objects must be a child of an existing model in your app (e.g. BlogPost). In order to allow attaching them to
your model, it must inherit from `CommentModelMixin`:

```python title="blog_post/models.py"
from django_spire.comment.mixins import CommentModelMixin

class BlogPost(CommentModelMixin):
    ...
```

## Including a Comment List in Your Detail Page

Simple include the `comment_list_card.html` template in your page's template, passing in the model instance that the
comments are attached to as `obj`:

```html title="blog_post/container/detail_container.html"
<!-- Other stuff -->
<div class="col-12 col-xl-6">
    {% include 'django_spire/comment/card/comment_list_card.html' with obj=blog_post %}
</div>
<!-- Other stuff -->
```

You should now have a fully fledged comment list card on your page that has all CRUD functionally.
 