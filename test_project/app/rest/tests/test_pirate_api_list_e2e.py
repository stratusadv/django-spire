from __future__ import annotations

import pytest

from typing import TYPE_CHECKING, Any

from playwright.sync_api import expect

from django_spire.contrib.rest.connector.exceptions import RestConnectorError
from django_spire.testing.playwright.components.scroll_component import ScrollComponent

from test_project.app.rest.rest import PirateRestSchema
from test_project.app.rest.rest.schemaset import PirateRestSchemaSet

if TYPE_CHECKING:
    from collections.abc import Callable

    from limelight import Demo
    from playwright.sync_api import Page


pytestmark = [pytest.mark.e2e, pytest.mark.playwright]

ROW_SELECTOR = '[data-scroll-key]'
NAME_SELECTOR = '[data-pirate-name]'


class FakePirateApi:
    """Stands in for the DummyJSON users endpoints, so no test reaches the network."""

    def __init__(self, count: int) -> None:
        self.read_many_params: list[dict[str, Any]] = []
        self.read_one_ids: list[int] = []
        self.users = {
            number: {
                'id': number,
                'firstName': 'Mate',
                'lastName': f'{number:02d}',
                'email': f'mate{number:02d}@example.com',
                'username': f'mate{number:02d}',
            }
            for number in range(1, count + 1)
        }

    def read_many(self, **request_params: Any) -> list[PirateRestSchema]:
        self.read_many_params.append(request_params)
        skip = request_params['skip']
        users = list(self.users.values())[skip:skip + request_params['limit']]

        return [PirateRestSchema(**user) for user in users]

    def read_one(self, **request_params: Any) -> PirateRestSchema:
        self.read_one_ids.append(int(request_params['id']))
        user = self.users.get(int(request_params['id']))

        if user is None:
            raise RestConnectorError

        return PirateRestSchema(**user)


@pytest.fixture
def pirate_api(monkeypatch: pytest.MonkeyPatch) -> FakePirateApi:
    api = FakePirateApi(count=60)

    monkeypatch.setattr(
        PirateRestSchemaSet,
        '_read_many',
        lambda _self, **request_params: api.read_many(**request_params),
    )
    monkeypatch.setattr(
        PirateRestSchemaSet,
        '_read_one',
        lambda _self, **request_params: api.read_one(**request_params),
    )

    return api


def test_scrolling_an_api_list_pages_through_the_api(
    page: Page,
    demo_start: Callable[..., Demo],
    transactional_db: None,
    pirate_api: FakePirateApi,
) -> None:
    del transactional_db

    demo = demo_start()
    demo.goto('rest:page:api_list')

    scroll = ScrollComponent(page, row_selector=ROW_SELECTOR)
    scroll.scroll_until_row_count(60)
    state = scroll.state()

    assert scroll.rows.locator(NAME_SELECTOR).all_inner_texts() == [
        f'Mate {number:02d}' for number in range(1, 61)
    ]
    assert state['loadedCount'] == 60
    assert state['hasMore'] is False
    assert pirate_api.read_many_params == [
        {'skip': 0, 'limit': 26},
        {'skip': 25, 'limit': 26},
        {'skip': 50, 'limit': 26},
    ]


def test_refreshing_one_api_row_fetches_only_that_pirate(
    page: Page,
    demo_start: Callable[..., Demo],
    transactional_db: None,
    pirate_api: FakePirateApi,
) -> None:
    del transactional_db

    demo = demo_start()
    demo.goto('rest:page:api_list')

    scroll = ScrollComponent(page, row_selector=ROW_SELECTOR)
    scroll.scroll_until_row_count(60)
    batches_read = len(pirate_api.read_many_params)

    pirate_api.users[3]['firstName'] = 'Captain'
    del pirate_api.users[4]

    page.evaluate(f"""
        async () => {{
            const scroll = {scroll.data_expression}

            await scroll.refreshItem(3)
            await scroll.refreshItem(4)
        }}
    """)

    expect(page.locator("[data-scroll-key='3']").locator(NAME_SELECTOR)).to_have_text('Captain 03')
    expect(page.locator("[data-scroll-key='4']")).to_have_count(0)
    assert scroll.row_count() == 59
    assert pirate_api.read_one_ids == [3, 4]
    assert len(pirate_api.read_many_params) == batches_read
