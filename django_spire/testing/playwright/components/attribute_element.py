from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class AttributeElement:
    """Playwright component for django_spire/element/attribute_element.html"""

    def __init__(self, page: Page, container_selector: str = 'body') -> None:
        self.container_selector = container_selector
        self.page = page

    @property
    def container(self) -> Locator:
        return self.page.locator(self.container_selector)

    def get_attribute_by_title(self, title: str) -> Locator:
        return self.container.locator(f'.fs-7.text-app-attribute-color:has-text("{title}")').locator('..')

    def get_value_by_title(self, title: str) -> str:
        attribute = self.get_attribute_by_title(title)
        return attribute.locator('.fs-6, a').inner_text()

    def get_value_href_by_title(self, title: str) -> str | None:
        attribute = self.get_attribute_by_title(title)
        link = attribute.locator('a')

        if link.count() > 0:
            return link.get_attribute('href')

        return None

    def has_attribute(self, title: str) -> bool:
        return self.get_attribute_by_title(title).count() > 0

    def is_value_link(self, title: str) -> bool:
        attribute = self.get_attribute_by_title(title)
        return attribute.locator('a').count() > 0


class AttributeList:
    """Helper for pages with multiple attribute elements"""

    def __init__(self, page: Page, container_selector: str = 'body') -> None:
        self.container_selector = container_selector
        self.page = page

    @property
    def container(self) -> Locator:
        return self.page.locator(self.container_selector)

    @property
    def attributes(self) -> Locator:
        return self.container.locator('.fs-7.text-app-attribute-color')

    def get_all_titles(self) -> list[str]:
        count = self.attributes.count()
        return [self.attributes.nth(i).inner_text() for i in range(count)]

    def get_attribute_count(self) -> int:
        return self.attributes.count()

    def get_values_dict(self) -> dict[str, str]:
        result = {}
        attr_element = AttributeElement(self.page, self.container_selector)

        for title in self.get_all_titles():
            result[title] = attr_element.get_value_by_title(title)

        return result
