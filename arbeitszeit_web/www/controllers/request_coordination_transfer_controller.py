from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from arbeitszeit.interactors.request_coordination_transfer import (
    RequestCoordinationTransferInteractor as Interactor,
)
from arbeitszeit_web.fields import parse_formfield
from arbeitszeit_web.forms import RequestCoordinationTransferForm
from arbeitszeit_web.session import Session
from arbeitszeit_web.www.formfield_parsers import UuidParser


@dataclass
class RequestCoordinationTransferController:
    session: Session
    uuid_parser: UuidParser

    def import_form_data(
        self, form: RequestCoordinationTransferForm
    ) -> Optional[Interactor.Request]:
        candidate = parse_formfield(form.candidate_field(), self.uuid_parser)
        cooperation = parse_formfield(form.cooperation_field(), self.uuid_parser)
        current_user = self.session.get_current_user()
        if not (candidate and cooperation and current_user):
            return None
        return Interactor.Request(
            requester=current_user,
            cooperation=cooperation.value,
            candidate=candidate.value,
        )
