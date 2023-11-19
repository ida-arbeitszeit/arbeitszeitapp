from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit.use_cases.request_coordination_transfer import (
    RequestCoordinationTransferUseCase as UseCase,
)
from arbeitszeit_web.forms import RequestCoordinationTransferForm


@dataclass
class RequestCoordinationTransferController:
    def import_form_data(
        self, form: RequestCoordinationTransferForm
    ) -> Optional[UseCase.Request]:
        try:
            candidate = UUID(form.candidate_field().get_value())
        except ValueError:
            return None
        try:
            requesting_tenure = UUID(form.requesting_tenure_field().get_value())
        except ValueError:
            return None
        return UseCase.Request(
            candidate=candidate,
            requesting_coordination_tenure=requesting_tenure,
        )
