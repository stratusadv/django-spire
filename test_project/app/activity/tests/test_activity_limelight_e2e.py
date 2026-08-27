from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from playwright.sync_api import expect

from limelight import DemoSession
from limelight.django import DjangoApplication

if TYPE_CHECKING:
    from playwright.sync_api import Page
    from pytest_django.live_server_helper import LiveServer


pytestmark = [pytest.mark.demo, pytest.mark.playwright]


def test_activity_lifecycle_demo(
    page: Page,
    live_server: LiveServer,
    transactional_db: None,
) -> None:
    del transactional_db

    user = get_user_model().objects.create_superuser(
        username='limelight',
    )
    application = DjangoApplication(live_server=live_server, user=user)
    demo = DemoSession.start(
        page,
        application,
        shot_directory_name='django-spire-activity-lifecycle',
    )

    demo.goto('activity:demo')
    expect(page.get_by_role('heading', name='Activity Demo')).to_be_visible()
    expect(page.locator('#demo-feed-empty')).to_be_visible()

    demo.title_card(
        'Automatic Activity History',
        kicker='django-spire',
        subtitle='Create, update, delete, and restore with an attributed audit trail.',
    )

    create_button = page.locator('#demo-create')
    demo.narrate(
        'Create a task',
        body='The request user is captured automatically by Spire activity middleware.',
        step='1',
    )
    demo.spotlight(create_button, label='Create')
    demo.click(create_button)
    expect(page.locator('#demo-task-count')).to_have_text('Demo Tasks: 1')
    expect(page.locator('.activity-feed-row [data-verb="created"]')).to_have_count(1)

    update_button = page.locator('#demo-update')
    demo.narrate(
        'Update the task',
        body='Saving the model adds an updated activity without explicit logging code.',
        step='2',
    )
    demo.spotlight(update_button, label='Update')
    demo.click(update_button)
    expect(page.locator('.activity-feed-row [data-verb="updated"]')).to_have_count(1)

    delete_button = page.locator('#demo-soft-delete')
    demo.narrate(
        'Soft-delete the task',
        body='The task remains recoverable and the feed records a deleted event.',
        step='3',
    )
    demo.spotlight(delete_button, label='Soft Delete')
    demo.click(delete_button)
    expect(page.locator('#demo-task-deleted-count')).to_have_text('Soft Deleted: 1')
    expect(page.locator('.activity-feed-row [data-verb="deleted"]')).to_have_count(1)

    restore_button = page.locator('#demo-restore')
    demo.narrate(
        'Restore the task',
        body='Restoring makes the task active again and records the state transition.',
        step='4',
    )
    demo.spotlight(restore_button, label='Restore')
    demo.click(restore_button)
    expect(page.locator('#demo-task-deleted-count')).to_have_text('Soft Deleted: 0')
    expect(page.locator('.activity-feed-row [data-verb="updated"]')).to_have_count(2)

    demo.narrate(
        'The complete audit trail',
        body='Every change is attributed to the authenticated user and visible in the feed.',
        kind='success',
    )
    activity_feed = page.locator('.card').filter(has_text='Activity Feed')
    expect(activity_feed).to_be_visible()
    demo.spotlight(activity_feed, label='Activity Feed')
