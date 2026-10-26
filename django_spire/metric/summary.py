from dataclasses import dataclass, field


@dataclass
class BuildSummary:
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    missing: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing and not self.errors
