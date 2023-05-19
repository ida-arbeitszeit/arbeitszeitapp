import enum
import os
from typing import Set, TypeVar

_MARKERS: Set[str] = {
    marker.strip() for marker in os.getenv("DISABLED_TESTS", "").split(",")
}

T = TypeVar("T")


class Category(enum.Enum):
    database_required = "database_required"


def _are_test_categories_enabled(*categories: Category) -> bool:
    return all(category.value not in _MARKERS for category in categories)


def database_required(cls: type[T]) -> type[T]:
    class DatabaseTests(cls):  # type: ignore
        def setUp(self) -> None:
            if not _are_test_categories_enabled(Category.database_required):
                self.skipTest("Tests that require a database connection are disabled")
            super().setUp()

    return DatabaseTests
