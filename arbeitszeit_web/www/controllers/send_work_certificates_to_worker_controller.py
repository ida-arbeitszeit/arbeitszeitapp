from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import Enum, auto
from typing import Union
from uuid import UUID

from arbeitszeit.use_cases.send_work_certificates_to_worker import (
    SendWorkCertificatesToWorkerRequest,
)
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session


@dataclass
class ControllerRejection:
    class RejectionReason(Exception, Enum):
        invalid_input = auto()
        negative_amount = auto()

    reason: RejectionReason


@dataclass
class SendWorkCertificatesToWorkerController:
    session: Session
    request: Request

    def create_use_case_request(
        self,
    ) -> Union[SendWorkCertificatesToWorkerRequest, ControllerRejection]:
        company_uuid = self.session.get_current_user()
        worker_id = self.request.get_form("member_id")
        amount_str = self.request.get_form("amount")
        if not all([company_uuid, worker_id, amount_str]):
            return ControllerRejection(
                reason=ControllerRejection.RejectionReason.invalid_input
            )
        assert company_uuid
        assert worker_id
        assert amount_str

        try:
            worker_uuid = UUID(worker_id.strip())
            amount = Decimal(amount_str)
        except (ValueError, InvalidOperation):
            return ControllerRejection(
                reason=ControllerRejection.RejectionReason.invalid_input
            )

        if amount < 0:
            return ControllerRejection(
                reason=ControllerRejection.RejectionReason.negative_amount
            )

        use_case_request = SendWorkCertificatesToWorkerRequest(
            company_uuid, worker_uuid, amount
        )
        return use_case_request
