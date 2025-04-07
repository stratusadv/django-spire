from __future__ import annotations

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import now

from django_spire.comment.querysets import CommentQuerySet
from django_spire.history.mixins import HistoryModelMixin


class Comment(HistoryModelMixin):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, editable=False)
    object_id = models.PositiveIntegerField(editable=False)
    content_object = GenericForeignKey('content_type', 'object_id')

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='children',
        related_query_name='child'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        editable=False,
        related_name='comment_list'
    )

    information = models.TextField(default='')
    created_datetime = models.DateTimeField(default=now, editable=False)
    is_edited = models.BooleanField(default=False, editable=False)

    objects = CommentQuerySet.as_manager()

    def __str__(self):
        return f'{self.information[0:10]}...'

    # def active_replies(self):
    #     return self.children.active()

    def find_user_list(self):
        from django.contrib.auth.models import User
        return User.objects.filter(username__in=self.scrape_username_list())

    def scrape_username_list(self):
        return [username[1:] for username in self.information.split() if username.startswith('@')]

    def send_notification(self):
        print('Function Called')
        # print(self.scrape_username_list())
        # print(self.find_user_list())
        for user in self.find_user_list():
            print(f'Sending comment to {user.username}')
            # create(
            #     user=user,
            #     head=f'{self.user.get_full_name()} commented on a task',
            #     subject='Business Base - New Comment',
            #     body=f'"{self.information}" on {self.content_object}',
            #     # Todo: Need to generate URL. Use generic reverse?
            #     url='',
            # )

    # Ordering by statistic_date_time_created creates duplicated results when querying because of generic relationship.
    def update(self, information):
        self.information = information
        self.is_edited = True
        self.save()

    class Meta:
        db_table = 'spire_comment'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-created_datetime']
