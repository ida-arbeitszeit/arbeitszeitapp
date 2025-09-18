from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from arbeitszeit.use_cases.request_coordination_transfer import (
    RequestCoordinationTransferUseCase as UseCase,
)
from arbeitszeit_web.forms import RequestCoordinationTransferForm
from arbeitszeit_web.forms.fields import parse_formfield
from arbeitszeit_web.forms.formfield_parsers import UuidParser
from arbeitszeit_web.session import Session


@dataclass
class RequestCoordinationTransferController:
    session: Session
    uuid_parser: UuidParser

    def import_form_data(
        self, form: RequestCoordinationTransferForm
    ) -> Optional[UseCase.Request]:
        candidate = parse_formfield(form.candidate_field(), self.uuid_parser)
        cooperation = parse_formfield(form.cooperation_field(), self.uuid_parser)
        current_user = self.session.get_current_user()
        if not (candidate and cooperation and current_user):
            return None
        return UseCase.Request(
            requester=current_user,
            cooperation=cooperation.value,
            candidate=candidate.value,
        )
