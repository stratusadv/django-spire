from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from playwright.sync_api import expect

from django.urls import reverse

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page
    from pytest_django.plugin import _LiveServer


pytestmark = pytest.mark.playwright


def activity_rows(page: Page) -> Locator:
    return page.locator('.activity-feed-row')


def click_action(page: Page, button_id: str) -> None:
    page.click(f'#{button_id}')
    page.wait_for_load_state('networkidle')


def open_demo(page: Page, live_server: _LiveServer) -> Page:
    page.goto(f'{live_server.url}{reverse("activity:demo")}')

    return page


def verb_rows(page: Page, verb: str) -> Locator:
    return page.locator(f'.activity-feed-row [data-verb="{verb}"]')


class TestActivityDemoWalkthrough:
    def test_every_action_logs_to_feed(
        self,
        authenticated_page: Page,
        live_server: _LiveServer,
    ) -> None:
        page = open_demo(authenticated_page, live_server)

        expect(page.locator('#demo-feed-empty')).to_be_visible()

        click_action(page, 'demo-create')
        expect(verb_rows(page, 'created')).to_have_count(1)

        click_action(page, 'demo-update')
        expect(verb_rows(page, 'updated')).to_have_count(1)

        click_action(page, 'demo-bulk-create')
        expect(verb_rows(page, 'created')).to_have_count(4)

        click_action(page, 'demo-bulk-update')
        expect(verb_rows(page, 'updated')).to_have_count(4)

        click_action(page, 'demo-queryset-update')
        expect(verb_rows(page, 'updated')).to_have_count(8)

        click_action(page, 'demo-soft-delete')
        expect(verb_rows(page, 'deleted')).to_have_count(1)
        expect(verb_rows(page, 'updated')).to_have_count(8)

        click_action(page, 'demo-restore')
        expect(verb_rows(page, 'deleted')).to_have_count(1)
        expect(verb_rows(page, 'updated')).to_have_count(9)

        click_action(page, 'demo-hard-delete')
        expect(verb_rows(page, 'deleted')).to_have_count(2)

        click_action(page, 'demo-queryset-delete')
        expect(verb_rows(page, 'deleted')).to_have_count(4)

        click_action(page, 'demo-member-add')
        expect(verb_rows(page, 'added')).to_have_count(1)
        expect(page.locator('#demo-member-status')).to_have_text('Member is in group')

        click_action(page, 'demo-member-add-many')
        expect(verb_rows(page, 'added')).to_have_count(2)

        click_action(page, 'demo-member-remove')
        expect(verb_rows(page, 'removed')).to_have_count(1)
        expect(page.locator('#demo-member-status')).to_have_text('Member not in group')

        click_action(page, 'demo-member-clear')
        expect(verb_rows(page, 'removed')).to_have_count(2)

        click_action(page, 'demo-reset')
        expect(page.locator('#demo-feed-empty')).to_be_visible()
        expect(activity_rows(page)).to_have_count(0)


class TestActivityDemoFeed:
    def test_feed_starts_empty(
        self,
        authenticated_page: Page,
        live_server: _LiveServer,
    ) -> None:
        page = open_demo(authenticated_page, live_server)

        expect(page.locator('#demo-feed-empty')).to_be_visible()
        expect(activity_rows(page)).to_have_count(0)
        expect(page.locator('#demo-task-count')).to_have_text('Demo Tasks: 0')
        expect(page.locator('#demo-activity-count')).to_have_text('Activities: 0')

    def test_feed_row_names_the_actor_and_the_object(
        self,
        authenticated_page: Page,
        live_server: _LiveServer,
    ) -> None:
        page = open_demo(authenticated_page, live_server)

        click_action(page, 'demo-create')

        newest_row = activity_rows(page).first

        expect(newest_row).to_contain_text('testuser created Task "Activity Demo Task 1".')
        expect(newest_row.locator('[data-verb="created"]')).to_be_visible()

    def test_counters_track_the_demo_state(
        self,
        authenticated_page: Page,
        live_server: _LiveServer,
    ) -> None:
        page = open_demo(authenticated_page, live_server)

        click_action(page, 'demo-create')
        expect(page.locator('#demo-task-count')).to_have_text('Demo Tasks: 1')
        expect(page.locator('#demo-activity-count')).to_have_text('Activities: 1')

        click_action(page, 'demo-soft-delete')
        expect(page.locator('#demo-task-deleted-count')).to_have_text('Soft Deleted: 1')
        expect(page.locator('#demo-activity-count')).to_have_text('Activities: 2')


class TestActivityDemoSingleObject:
    def test_soft_delete_then_restore_logs_deleted_then_updated(
        self,
        authenticated_page: Page,
        live_server: _LiveServer,
    ) -> None:
        page = open_demo(authenticated_page, live_server)

        click_action(page, 'demo-create')
        click_action(page, 'demo-soft-delete')

        expect(verb_rows(page, 'deleted')).to_have_count(1)
        expect(page.locator('#demo-task-deleted-count')).to_have_text('Soft Deleted: 1')

        click_action(page, 'demo-restore')

        expect(verb_rows(page, 'updated')).to_have_count(1)
        expect(verb_rows(page, 'deleted')).to_have_count(1)
        expect(page.locator('#demo-task-deleted-count')).to_have_text('Soft Deleted: 0')

    def test_hard_delete_leaves_only_the_tombstone(
        self,
        authenticated_page: Page,
        live_server: _LiveServer,
    ) -> None:
        page = open_demo(authenticated_page, live_server)

        click_action(page, 'demo-create')
        click_action(page, 'demo-update')

        expect(activity_rows(page)).to_have_count(2)

        click_action(page, 'demo-hard-delete')

        expect(activity_rows(page)).to_have_count(1)
        expect(verb_rows(page, 'deleted')).to_have_count(1)
        expect(verb_rows(page, 'created')).to_have_count(0)
        expect(page.locator('#demo-task-count')).to_have_text('Demo Tasks: 0')

    def test_cascade_delete_logs_the_parent_and_the_child(
        self,
        authenticated_page: Page,
        live_server: _LiveServer,
    ) -> None:
        page = open_demo(authenticated_page, live_server)

        click_action(page, 'demo-create')
        click_action(page, 'demo-child-create')

        expect(verb_rows(page, 'created')).to_have_count(2)
        expect(page.locator('#demo-task-count')).to_have_text('Demo Tasks: 2')

        click_action(page, 'demo-cascade-delete')

        expect(verb_rows(page, 'deleted')).to_have_count(2)
        expect(verb_rows(page, 'created')).to_have_count(0)
        expect(page.locator('#demo-task-count')).to_have_text('Demo Tasks: 0')


class TestActivityDemoBulk:
    def test_bulk_create_logs_one_row_per_task(
        self,
        authenticated_page: Page,
        live_server: _LiveServer,
    ) -> None:
        page = open_demo(authenticated_page, live_server)

        click_action(page, 'demo-bulk-create')

        expect(verb_rows(page, 'created')).to_have_count(3)
        expect(page.locator('#demo-task-count')).to_have_text('Demo Tasks: 3')

    def test_bulk_update_logs_one_row_per_task(
        self,
        authenticated_page: Page,
        live_server: _LiveServer,
    ) -> None:
        page = open_demo(authenticated_page, live_server)

        click_action(page, 'demo-bulk-create')
        click_action(page, 'demo-bulk-update')

        expect(verb_rows(page, 'updated')).to_have_count(3)

    def test_queryset_update_logs_one_row_per_task(
        self,
        authenticated_page: Page,
        live_server: _LiveServer,
    ) -> None:
        page = open_demo(authenticated_page, live_server)

        click_action(page, 'demo-bulk-create')
        click_action(page, 'demo-queryset-update')

        expect(verb_rows(page, 'updated')).to_have_count(3)

    def test_queryset_delete_logs_one_row_per_task(
        self,
        authenticated_page: Page,
        live_server: _LiveServer,
    ) -> None:
        page = open_demo(authenticated_page, live_server)

        click_action(page, 'demo-bulk-create')
        click_action(page, 'demo-queryset-delete')

        expect(verb_rows(page, 'deleted')).to_have_count(3)
        expect(page.locator('#demo-task-count')).to_have_text('Demo Tasks: 0')


class TestActivityDemoMembership:
    def test_first_add_also_logs_the_group_creation(
        self,
        authenticated_page: Page,
        live_server: _LiveServer,
    ) -> None:
        page = open_demo(authenticated_page, live_server)

        click_action(page, 'demo-member-add')

        expect(verb_rows(page, 'created')).to_have_count(1)
        expect(verb_rows(page, 'added')).to_have_count(1)
        expect(page.locator('#demo-group-member-count')).to_have_text('Group Members: 1')

    def test_add_many_members_logs_a_single_counted_row(
        self,
        authenticated_page: Page,
        live_server: _LiveServer,
    ) -> None:
        page = open_demo(authenticated_page, live_server)

        click_action(page, 'demo-member-add')
        click_action(page, 'demo-member-add-many')

        expect(verb_rows(page, 'added')).to_have_count(2)
        expect(activity_rows(page).first).to_contain_text('added 3 users')
        expect(page.locator('#demo-group-member-count')).to_have_text('Group Members: 4')

    def test_clear_members_logs_a_single_counted_row(
        self,
        authenticated_page: Page,
        live_server: _LiveServer,
    ) -> None:
        page = open_demo(authenticated_page, live_server)

        click_action(page, 'demo-member-add')
        click_action(page, 'demo-member-add-many')
        click_action(page, 'demo-member-clear')

        expect(verb_rows(page, 'removed')).to_have_count(1)
        expect(activity_rows(page).first).to_contain_text('removed 4 users')
        expect(page.locator('#demo-group-member-count')).to_have_text('Group Members: 0')

    def test_remove_updates_the_membership_badge(
        self,
        authenticated_page: Page,
        live_server: _LiveServer,
    ) -> None:
        page = open_demo(authenticated_page, live_server)

        click_action(page, 'demo-member-add')
        expect(page.locator('#demo-member-status')).to_have_text('Member is in group')

        click_action(page, 'demo-member-remove')
        expect(page.locator('#demo-member-status')).to_have_text('Member not in group')
        expect(verb_rows(page, 'removed')).to_have_count(1)


class TestActivityDemoAttribution:
    def test_unattributed_create_adds_a_task_without_activity(
        self,
        authenticated_page: Page,
        live_server: _LiveServer,
    ) -> None:
        page = open_demo(authenticated_page, live_server)

        click_action(page, 'demo-unattributed-create')

        expect(page.locator('#demo-task-count')).to_have_text('Demo Tasks: 1')
        expect(page.locator('#demo-feed-empty')).to_be_visible()
        expect(activity_rows(page)).to_have_count(0)

    def test_only_the_attributed_create_reaches_the_feed(
        self,
        authenticated_page: Page,
        live_server: _LiveServer,
    ) -> None:
        page = open_demo(authenticated_page, live_server)

        click_action(page, 'demo-create')
        expect(activity_rows(page)).to_have_count(1)

        click_action(page, 'demo-unattributed-create')

        expect(page.locator('#demo-task-count')).to_have_text('Demo Tasks: 2')
        expect(activity_rows(page)).to_have_count(1)


class TestActivityDemoReset:
    def test_reset_clears_tasks_members_and_the_feed(
        self,
        authenticated_page: Page,
        live_server: _LiveServer,
    ) -> None:
        page = open_demo(authenticated_page, live_server)

        click_action(page, 'demo-bulk-create')
        click_action(page, 'demo-member-add')
        click_action(page, 'demo-member-add-many')

        click_action(page, 'demo-reset')

        expect(page.locator('#demo-feed-empty')).to_be_visible()
        expect(activity_rows(page)).to_have_count(0)
        expect(page.locator('#demo-task-count')).to_have_text('Demo Tasks: 0')
        expect(page.locator('#demo-group-member-count')).to_have_text('Group Members: 0')
