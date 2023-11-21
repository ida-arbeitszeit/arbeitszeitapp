from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit.use_cases.request_coordination_transfer import (
    RequestCoordinationTransferUseCase as UseCase,
)
from arbeitszeit_web.forms import RequestCoordinationTransferForm
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator


@dataclass
class RequestCoordinationTransferController:
    session: Session
    request: Request
    translator: Translator

    def import_form_data(
        self, form: RequestCoordinationTransferForm
    ) -> Optional[UseCase.Request]:
        try:
            candidate = UUID(form.candidate_field().get_value())
        except ValueError:
            form.candidate_field().attach_error(self.translator.gettext("Invalid UUID"))
            return None
        try:
            cooperation = UUID(form.cooperation_field().get_value())
        except ValueError:
            form.cooperation_field().attach_error(
                self.translator.gettext("Invalid UUID")
            )
            return None
        current_user = self.session.get_current_user()
        assert current_user
        return UseCase.Request(
            requester=current_user,
            cooperation=cooperation,
            candidate=candidate,
        )
