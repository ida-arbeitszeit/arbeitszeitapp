from dataclasses import dataclass
from typing import List
from urllib.parse import urlencode, urlparse, urlunparse

from arbeitszeit_web.request import Request

PAGE_PARAMETER_NAME = "page"
"""The name of the request query parameter used for pagination."""

DEFAULT_PAGE_SIZE = 15


@dataclass
class PageLink:
    label: str
    href: str
    is_current: bool


@dataclass
class Pagination:
    is_visible: bool
    pages: List[PageLink]


class Paginator:
    def __init__(
        self,
        request: Request,
        total_results: int,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> None:
        self.parsed_url = urlparse(request.get_request_target())
        self.query_arguments: dict[str, str] = dict(request.query_string().items())
        self.page_size = page_size
        self.total_results = total_results
        self.current_offset = calculate_current_offset(request, self.page_size)

    def get_page_link(self, page: int) -> str:
        query = dict(self.query_arguments)
        query[PAGE_PARAMETER_NAME] = str(page)
        modified_parsed = self.parsed_url._replace(query=urlencode(query))
        return urlunparse(modified_parsed)

    def get_pages(self) -> List[PageLink]:
        current_page_number = 1 + self.current_offset // self.page_size
        return [
            PageLink(
                label=str(n),
                href=self.get_page_link(page=n),
                is_current=current_page_number == n,
            )
            for n in range(1, self.number_of_pages + 1)
        ]

    @property
    def number_of_pages(self) -> int:
        return 1 + (self.total_results - 1) // self.page_size


def calculate_current_offset(request: Request, limit: int) -> int:
    page_number_str = request.query_string().get_last_value(PAGE_PARAMETER_NAME)
    if page_number_str is None:
        return 0
    try:
        page_number = int(page_number_str)
    except ValueError:
        return 0
    return (page_number - 1) * limit
