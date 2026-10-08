from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from playwright.sync_api import expect

from django_spire.testing.playwright.components.scroll_component import ScrollComponent

from test_project.app.task.choices import TaskStatusChoices
from test_project.app.task.models import Task
from test_project.app.task.tests.factories import create_test_task

if TYPE_CHECKING:
    from collections.abc import Callable

    from limelight import Demo
    from playwright.sync_api import Locator, Page


pytestmark = [pytest.mark.e2e, pytest.mark.playwright]

ROW_SELECTOR = '[data-task-key]'
NAME_SELECTOR = '[data-task-name]'


def _open_task_list(page: Page, demo_start: Callable[..., Demo], row_count: int) -> ScrollComponent:
    demo = demo_start()
    demo.goto('task:page:list_component')

    scroll = ScrollComponent(page, row_selector=ROW_SELECTOR)
    scroll.wait_for_row_count(row_count)
    scroll.wait_until_idle()

    return scroll


def _row(page: Page, task: Task) -> Locator:
    return page.locator(f"[data-task-key='{task.pk}']")


def test_the_status_and_ordering_controls_reload_the_list(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    create_test_task(name='Alpha Task', status=TaskStatusChoices.NEW)
    create_test_task(name='Bravo Task', status=TaskStatusChoices.DONE)
    create_test_task(name='Charlie Task', status=TaskStatusChoices.NEW)

    scroll = _open_task_list(page, demo_start, row_count=3)

    assert scroll.rows.locator(NAME_SELECTOR).all_inner_texts() == [
        'Alpha Task',
        'Bravo Task',
        'Charlie Task',
    ]

    page.get_by_label('Status', exact=True).select_option(TaskStatusChoices.DONE)
    scroll.wait_for_row_count(1)
    scroll.wait_until_idle()

    assert scroll.rows.locator(NAME_SELECTOR).all_inner_texts() == ['Bravo Task']

    page.get_by_label('Status', exact=True).select_option('')
    scroll.wait_for_row_count(3)
    page.get_by_label('Order').select_option('-name')
    expect(scroll.rows.first.locator(NAME_SELECTOR)).to_have_text('Charlie Task')
    scroll.wait_until_idle()

    assert scroll.rows.locator(NAME_SELECTOR).all_inner_texts() == [
        'Charlie Task',
        'Bravo Task',
        'Alpha Task',
    ]
    expect(page.get_by_label('Order')).to_have_value('-name')


def test_scrolling_and_reloading_glue_rows_keeps_the_list_whole_and_releases_dropped_rows(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    tasks = [
        create_test_task(name=f'Task {number:02d}', status=TaskStatusChoices.NEW)
        for number in range(1, 61)
    ]
    names = [task.name for task in tasks]

    scroll = _open_task_list(page, demo_start, row_count=25)
    search = page.get_by_placeholder('Search tasks ...')
    scroll_facts = f"""
        () => {{
            const scroll = {scroll.data_expression}

            return {{
                hasMore: scroll.hasMore,
                loadedCount: scroll.loadedCount,
                liveRecords: scroll.component._registry.records.size,
            }}
        }}
    """

    scroll.scroll_until_row_count(60)
    first_pass = page.evaluate(scroll_facts)

    assert scroll.rows.locator(NAME_SELECTOR).all_inner_texts() == names
    assert first_pass['hasMore'] is False
    assert first_pass['loadedCount'] == 60

    live_records_after_each_reload = []

    for search_term in ('Task', 'task', 'Task'):
        generation = page.evaluate(f'() => {scroll.data_expression}.loadGeneration')

        search.fill(search_term)
        page.wait_for_function(
            f"""
                (generation) => {{
                    const scroll = {scroll.data_expression}

                    return scroll.loadGeneration > generation && !scroll.isLoading
                }}
            """,
            arg=generation,
        )
        scroll.scroll_until_row_count(60)

        assert scroll.rows.locator(NAME_SELECTOR).all_inner_texts() == names

        live_records_after_each_reload.append(page.evaluate(scroll_facts)['liveRecords'])

    rows_forms_batches_and_the_list = 60 + 60 + 3 + 1

    assert [first_pass['liveRecords'], *live_records_after_each_reload] == [
        rows_forms_batches_and_the_list
    ] * 4

    _row(page, tasks[-1]).get_by_title('Complete Task').click()

    expect(_row(page, tasks[-1]).get_by_label('Task status')).to_have_value(TaskStatusChoices.DONE)
    assert scroll.row_count() == 60


def test_completing_a_task_updates_its_row_and_leaves_the_others_in_place(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    alpha = create_test_task(name='Alpha Task', status=TaskStatusChoices.NEW)
    bravo = create_test_task(name='Bravo Task', status=TaskStatusChoices.NEW)

    scroll = _open_task_list(page, demo_start, row_count=2)

    _row(page, bravo).evaluate("row => { row.dataset.untouched = 'yes' }")
    _row(page, alpha).get_by_title('Complete Task').click()

    expect(_row(page, alpha).get_by_label('Task status')).to_have_value(TaskStatusChoices.DONE)
    expect(_row(page, alpha).get_by_title('Complete Task')).to_be_hidden()
    expect(_row(page, bravo)).to_have_attribute('data-untouched', 'yes')
    expect(_row(page, bravo).get_by_label('Task status')).to_have_value(TaskStatusChoices.NEW)

    assert scroll.row_count() == 2
    assert Task.objects.get(pk=alpha.pk).status == TaskStatusChoices.DONE


def test_changing_a_rows_status_saves_the_task(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    alpha = create_test_task(name='Alpha Task', status=TaskStatusChoices.NEW)
    bravo = create_test_task(name='Bravo Task', status=TaskStatusChoices.NEW)

    scroll = _open_task_list(page, demo_start, row_count=2)

    with page.expect_response(lambda response: '__dg__' in response.url) as save_response:
        _row(page, alpha).get_by_label('Task status').select_option(TaskStatusChoices.IN_PROGRESS)

    assert 'save_model_obj' in save_response.value.request.post_data
    assert Task.objects.get(pk=alpha.pk).status == TaskStatusChoices.IN_PROGRESS

    expect(_row(page, alpha).get_by_label('Task status')).to_have_value(
        TaskStatusChoices.IN_PROGRESS
    )
    expect(_row(page, bravo).get_by_label('Task status')).to_have_value(TaskStatusChoices.NEW)
    assert scroll.row_count() == 2


def test_a_rows_form_refuses_an_invalid_edit_and_reports_it_on_the_row(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    alpha = create_test_task(name='Alpha Task', status=TaskStatusChoices.NEW)

    scroll = _open_task_list(page, demo_start, row_count=1)

    outcome = page.evaluate(f"""
        async () => {{
            const form = {scroll.data_expression}.items[0].form

            form.name = ''
            await form.validate()

            const nameHadErrors = form.hasErrors('name')
            const statusHadErrors = form.hasErrors('status')

            await form.save_model_obj()

            return {{nameHadErrors, statusHadErrors}}
        }}
    """)

    assert outcome == {'nameHadErrors': True, 'statusHadErrors': False}
    assert Task.objects.get(pk=alpha.pk).name == 'Alpha Task'
    assert scroll.row_count() == 1


def test_a_changed_task_that_no_longer_matches_the_filter_leaves_the_list(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    alpha = create_test_task(name='Alpha Task', status=TaskStatusChoices.NEW)
    bravo = create_test_task(name='Bravo Task', status=TaskStatusChoices.NEW)
    create_test_task(name='Charlie Task', status=TaskStatusChoices.DONE)

    scroll = _open_task_list(page, demo_start, row_count=3)

    page.get_by_label('Status', exact=True).select_option(TaskStatusChoices.NEW)
    scroll.wait_for_row_count(2)
    scroll.wait_until_idle()

    _row(page, alpha).get_by_title('Complete Task').click()
    scroll.wait_for_row_count(1)

    expect(_row(page, bravo)).to_be_visible()
    assert scroll.row_count() == 1


def test_duplicating_a_task_adds_the_copy_to_the_top_of_the_list(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    create_test_task(name='Alpha Task', status=TaskStatusChoices.NEW)
    bravo = create_test_task(name='Bravo Task', status=TaskStatusChoices.NEW)

    scroll = _open_task_list(page, demo_start, row_count=2)

    _row(page, bravo).get_by_title('Duplicate Task').click()
    scroll.wait_for_row_count(3)

    assert scroll.rows.locator(NAME_SELECTOR).all_inner_texts() == [
        'Bravo Task (Copy)',
        'Alpha Task',
        'Bravo Task',
    ]


def test_a_task_added_through_the_modal_appears_at_the_top_of_the_list(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    create_test_task(name='Alpha Task', status=TaskStatusChoices.NEW)
    bravo = create_test_task(name='Bravo Task', status=TaskStatusChoices.NEW)

    scroll = _open_task_list(page, demo_start, row_count=2)
    modal = page.locator('#baseDispatchModal')

    _row(page, bravo).evaluate("row => { row.dataset.untouched = 'yes' }")
    page.get_by_role('button', name='New Task').click()
    modal.locator('input[type="text"]').first.fill('Modal Made Task')
    modal.locator('textarea').first.fill('Made in the modal')
    modal.get_by_role('button', name='Submit').click()
    scroll.wait_for_row_count(3)

    assert scroll.rows.locator(NAME_SELECTOR).all_inner_texts() == [
        'Modal Made Task',
        'Alpha Task',
        'Bravo Task',
    ]
    expect(_row(page, bravo)).to_have_attribute('data-untouched', 'yes')
    expect(modal).to_be_hidden()
    assert Task.objects.filter(name='Modal Made Task').count() == 1


def test_a_task_edited_through_the_modal_updates_its_row(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    alpha = create_test_task(name='Alpha Task', status=TaskStatusChoices.NEW)
    bravo = create_test_task(name='Bravo Task', status=TaskStatusChoices.NEW)

    scroll = _open_task_list(page, demo_start, row_count=2)
    modal = page.locator('#baseDispatchModal')
    name_input = modal.locator('input[type="text"]').first

    _row(page, bravo).evaluate("row => { row.dataset.untouched = 'yes' }")
    _row(page, alpha).get_by_title('Edit Task').click()
    expect(name_input).to_have_value('Alpha Task')
    name_input.fill('Alpha Task Renamed')
    modal.get_by_role('button', name='Submit').click()

    expect(_row(page, alpha).locator(NAME_SELECTOR)).to_have_text('Alpha Task Renamed')
    expect(_row(page, bravo)).to_have_attribute('data-untouched', 'yes')
    expect(modal).to_be_hidden()
    assert scroll.row_count() == 2
    assert Task.objects.get(pk=alpha.pk).name == 'Alpha Task Renamed'


def test_expanding_a_task_loads_its_children_as_a_nested_list(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    parent = create_test_task(name='Alpha Task', status=TaskStatusChoices.NEW)
    childless = create_test_task(name='Bravo Task', status=TaskStatusChoices.NEW)
    child_names = [f'Child {number:02d}' for number in range(1, 13)]

    children = [
        create_test_task(name=child_name, parent_id=parent.pk, status=TaskStatusChoices.NEW)
        for child_name in child_names
    ]

    scroll = _open_task_list(page, demo_start, row_count=2)
    child_rows = _row(page, parent).locator(ROW_SELECTOR)
    parent_toggle = _row(page, parent).get_by_title('Toggle Child Tasks').first

    expect(_row(page, childless).get_by_title('Toggle Child Tasks')).to_be_hidden()

    parent_toggle.click()
    expect(child_rows).to_have_count(12)

    assert child_rows.locator(NAME_SELECTOR).all_inner_texts() == child_names
    assert page.evaluate(f'() => {scroll.data_expression}.loadedCount') == 2

    _row(page, children[0]).get_by_title('Complete Task').click()

    expect(_row(page, children[0]).get_by_label('Task status')).to_have_value(
        TaskStatusChoices.DONE
    )
    expect(child_rows).to_have_count(12)

    parent_toggle.click()
    expect(child_rows.first).to_be_hidden()


def _open_child_list(
    page: Page, demo_start: Callable[..., Demo], child_count: int
) -> tuple[Task, list[Task]]:
    parent = create_test_task(name='Alpha Task', status=TaskStatusChoices.NEW)
    children = [
        create_test_task(
            name=f'Child {number:02d}',
            parent_id=parent.pk,
            status=TaskStatusChoices.NEW,
        )
        for number in range(1, child_count + 1)
    ]

    _open_task_list(page, demo_start, row_count=1)
    _row(page, parent).get_by_title('Toggle Child Tasks').first.click()
    expect(_row(page, parent).locator(ROW_SELECTOR)).to_have_count(child_count)

    return parent, children


def test_a_child_task_is_edited_through_the_child_lists_own_form_component(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    parent, children = _open_child_list(page, demo_start, child_count=3)
    modal = page.locator('#baseDispatchModal')
    name_input = modal.locator('input[type="text"]').first

    _row(page, children[0]).get_by_title('Edit Task').click()
    expect(name_input).to_have_value('Child 01')
    name_input.fill('Child 01 Renamed')
    modal.get_by_role('button', name='Submit').click()

    expect(_row(page, children[0]).locator(NAME_SELECTOR)).to_have_text('Child 01 Renamed')
    expect(modal).to_be_hidden()
    expect(_row(page, parent).locator(ROW_SELECTOR)).to_have_count(3)
    assert Task.objects.get(pk=children[0].pk).name == 'Child 01 Renamed'


def test_detaching_a_child_task_takes_it_out_of_the_child_list(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    parent, children = _open_child_list(page, demo_start, child_count=3)
    child_rows = _row(page, parent).locator(ROW_SELECTOR)

    _row(page, children[1]).evaluate("row => { row.dataset.untouched = 'yes' }")
    _row(page, children[0]).get_by_title('Detach From Parent').click()
    expect(child_rows).to_have_count(2)

    expect(_row(page, children[1])).to_have_attribute('data-untouched', 'yes')
    assert child_rows.locator(NAME_SELECTOR).all_inner_texts() == ['Child 02', 'Child 03']

    detached = Task.objects.get(pk=children[0].pk)

    assert detached.parent_id is None
    assert detached.is_deleted is False


def test_an_action_given_something_that_is_not_an_item_says_so(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    create_test_task(name='Alpha Task', status=TaskStatusChoices.NEW)

    scroll = _open_task_list(page, demo_start, row_count=1)

    message = page.evaluate(f"""
        async () => {{
            try {{
                await {scroll.data_expression}.editItem({{name: 'Not In The List'}})
            }}
            catch (error) {{
                return error.message
            }}

            return null
        }}
    """)

    assert message == 'A scroll action was given an object that is not one of its items.'
    expect(page.locator('#baseDispatchModal')).to_be_hidden()


def test_deleting_a_task_removes_its_row(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    alpha = create_test_task(name='Alpha Task', status=TaskStatusChoices.NEW)
    bravo = create_test_task(name='Bravo Task', status=TaskStatusChoices.NEW)

    scroll = _open_task_list(page, demo_start, row_count=2)

    modal = page.locator('#baseDispatchModal')

    _row(page, alpha).get_by_title('Delete Task').click()
    expect(modal).to_contain_text('Alpha Task')
    modal.get_by_role('button', name='Cancel').click()
    expect(modal).to_be_hidden()

    assert scroll.row_count() == 2
    assert Task.objects.get(pk=alpha.pk).is_deleted is False

    _row(page, alpha).get_by_title('Delete Task').click()
    modal.get_by_role('button', name='Delete').click()
    scroll.wait_for_row_count(1)

    expect(modal).to_be_hidden()
    expect(_row(page, bravo)).to_be_visible()
    assert Task.objects.get(pk=alpha.pk).is_deleted is True
