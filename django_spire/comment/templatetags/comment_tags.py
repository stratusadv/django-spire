from django import template

register = template.Library()


@register.simple_tag()
def comment_form(related_obj, return_url, user, comment=None, parent=None, user_list=None):
    from django_spire.comment.forms import CommentForm
    return CommentForm(related_obj, return_url, user, instance=comment, parent=parent, user_list=user_list)


@register.simple_tag()
def user_list_from_content_type(related_obj):
    from django_spire.comment.utils import find_user_list_from_content_type
    return find_user_list_from_content_type(related_obj._meta.app_label, related_obj._meta.model_name)
