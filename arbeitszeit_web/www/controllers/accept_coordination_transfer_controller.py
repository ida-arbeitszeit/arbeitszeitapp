from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.use_cases.accept_coordination_transfer import (
    AcceptCoordinationTransferUseCase,
)
from arbeitszeit_web.session import Session

UseCaseRequest = AcceptCoordinationTransferUseCase.Request


@dataclass
class AcceptCoordinationTransferController:
    session: Session

    def create_use_case_request(self, transfer_request: UUID) -> UseCaseRequest:
        current_user = self.session.get_current_user()
        assert current_user
        return UseCaseRequest(
            transfer_request_id=transfer_request, accepting_company=current_user
        )
