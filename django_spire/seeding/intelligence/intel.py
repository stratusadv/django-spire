from dandy.intel import BaseIntel


class AttrsIntel(BaseIntel):
    items: list[str]


class SeedingIntel(BaseIntel):
    items: list[dict]

    def __iter__(self):
        return iter(self.items)
