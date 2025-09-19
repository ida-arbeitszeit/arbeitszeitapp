from dataclasses import dataclass

from arbeitszeit.interactors.list_transfers import Request as InteractorRequest
from arbeitszeit_web.pagination import (
    DEFAULT_PAGE_SIZE,
    calculate_current_offset,
)
from arbeitszeit_web.request import Request


@dataclass
class ListTransfersController:
    request: Request

    def create_interactor_request(self) -> InteractorRequest:
        offset = calculate_current_offset(request=self.request, limit=DEFAULT_PAGE_SIZE)
        return InteractorRequest(
            offset=offset,
            limit=DEFAULT_PAGE_SIZE,
        )
