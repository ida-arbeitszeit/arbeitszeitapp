import shutil
import subprocess
from logging import getLogger
from typing import Generator, Iterable, TypeVar

LOGGER = getLogger(__name__)


TARGET_PACKAGES = [
    "deepdiff",
    "flask_babel",
    "flask_login",
    "flask_mail",
    "flask_migrate",
    "flask_profiler",
    "flask_restx",
    "flask_sqlalchemy",
    "flask_talisman",
    "flask_wtf",
    "is_safe_url",
    "matplotlib",
    "parameterized",
    "wtforms",
]
T = TypeVar("T")


def main():
    LOGGER.info("Update type stubs from dependencies")
    packages = list(flatten(["-p", package_name] for package_name in TARGET_PACKAGES))
    shutil.rmtree("type_stubs")
    subprocess.run(["stubgen", "-o", "type_stubs"] + packages)


def flatten(list_of_lists: Iterable[Iterable[T]]) -> Generator[T, None, None]:
    for items in list_of_lists:
        yield from items


if __name__ == "__main__":
    main()
