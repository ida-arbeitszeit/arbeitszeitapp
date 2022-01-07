from dataclasses import dataclass
from typing import Protocol, Union
from uuid import UUID

from arbeitszeit.use_cases import AnswerCompanyWorkInviteRequest

from .malformed_input_data import MalformedInputData
from .session import Session


class AnswerCompanyWorkInviteForm(Protocol):
    def get_invite_id_field(self) -> str:
        ...

    def get_is_accepted_field(self) -> bool:
        ...


@dataclass(frozen=True)
class AnswerCompanyWorkInviteController:
    session: Session

    def import_form_data(
        self, form: AnswerCompanyWorkInviteForm
    ) -> Union[None, MalformedInputData, AnswerCompanyWorkInviteRequest]:
        try:
            invite_id = UUID(form.get_invite_id_field())
        except ValueError:
            return MalformedInputData("", "")
        requesting_user = self.session.get_current_user()
        if requesting_user is not None:
            return AnswerCompanyWorkInviteRequest(
                form.get_is_accepted_field(), invite_id, requesting_user
            )
        else:
            return None
