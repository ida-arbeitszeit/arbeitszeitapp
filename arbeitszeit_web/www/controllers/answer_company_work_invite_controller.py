from dataclasses import dataclass
from typing import Protocol, Union
from uuid import UUID

from arbeitszeit.use_cases.answer_company_work_invite import (
    AnswerCompanyWorkInviteRequest,
)
from arbeitszeit_web.malformed_input_data import MalformedInputData
from arbeitszeit_web.session import Session


class AnswerCompanyWorkInviteForm(Protocol):
    def get_is_accepted_field(self) -> bool: ...


@dataclass(frozen=True)
class AnswerCompanyWorkInviteController:
    session: Session

    def import_form_data(
        self, form: AnswerCompanyWorkInviteForm, invite_id: UUID
    ) -> Union[None, MalformedInputData, AnswerCompanyWorkInviteRequest]:
        requesting_user = self.session.get_current_user()
        if requesting_user is not None:
            return AnswerCompanyWorkInviteRequest(
                form.get_is_accepted_field(), invite_id, requesting_user
            )
        else:
            return None
