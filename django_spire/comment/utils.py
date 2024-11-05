from __future__ import annotations


def find_user_list_from_content_type(app_label, model_name):
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.auth.models import Permission, Group, User

    content_type = ContentType.objects.get(app_label=app_label, model=model_name)
    permission = Permission.objects.get(content_type=content_type, codename=f'view_{model_name}')
    groups = Group.objects.filter(permissions=permission)

    return User.objects.filter(groups__in=groups).distinct()


def generate_comment_user_list_data(user_list):
    user_data = []

    for user in user_list:
        user_data.append({
            'full_name': user.get_full_name().replace(' ', '_'),
            'id': user.pk,
        })

    return user_data


def parse_user_id_to_int_list(user_id_str):
    from django.contrib.auth.models import User

    user_id_list =  [int(user_id) for user_id in user_id_str.split(',')]
    return User.objects.filter(id__in=user_id_list)


def process_comment_notifications(user_list, comment_information, related_obj, user_commenting):
    from django_spire.notification.models import Notification
    from django.contrib.sites.models import Site

    for user in user_list:
        if user != user_commenting:
            Notification.create(
                email=user.email,
                title='New Comment',
                body=f'You were tagged in a new comment! {user_commenting.get_full_name()} wrote "{comment_information}" on {related_obj}.',
                url=Site.objects.get_current()
            )
