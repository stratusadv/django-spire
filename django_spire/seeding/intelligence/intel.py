from dandy.intel import BaseIntel


class SeedingIntel(BaseIntel):
    items: list[dict]

    def __iter__(self):
        return iter(self.items)


class SourceIntel(BaseIntel):
    file_name: str
    python_source_code: str
