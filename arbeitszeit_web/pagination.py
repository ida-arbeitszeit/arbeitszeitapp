from dataclasses import dataclass
from typing import Dict, List
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

PAGE_PARAMETER_NAME = "page"
"""The name of the request query parameter used for pagination."""


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
        base_url: str,
        query_arguments: Dict[str, str],
        page_size: int,
        total_results: int,
        current_offset: int,
    ) -> None:
        self.parsed_url = urlparse(base_url)
        self.query_arguments = query_arguments
        self.parsed_query_arguments: Dict[str, str] = {
            key: values[0] for key, values in parse_qs(self.parsed_url.query).items()
        }
        self.parsed_query_arguments.update(query_arguments)
        self.page_size = page_size
        self.total_results = total_results
        self.current_offset = current_offset

    def get_page_link(self, page: int) -> str:
        query = dict(self.parsed_query_arguments)
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
            for n in range(1, self.page_count + 1)
        ]

    @property
    def page_count(self) -> int:
        return 1 + (self.total_results - 1) // self.page_size
