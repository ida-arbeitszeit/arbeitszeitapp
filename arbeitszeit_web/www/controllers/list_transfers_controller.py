from dataclasses import dataclass

from arbeitszeit.use_cases.list_transfers import Request as UseCaseRequest
from arbeitszeit_web.pagination import (
    DEFAULT_PAGE_SIZE,
    calculate_current_offset,
)
from arbeitszeit_web.request import Request


@dataclass
class ListTransfersController:
    request: Request

    def create_use_case_request(self) -> UseCaseRequest:
        offset = calculate_current_offset(request=self.request, limit=DEFAULT_PAGE_SIZE)
        return UseCaseRequest(
            offset=offset,
            limit=DEFAULT_PAGE_SIZE,
        )
