from dataclasses import dataclass
from typing import Any, Optional, Protocol, Union
from uuid import UUID, uuid4

from arbeitszeit.use_cases import AnswerCompanyWorkInviteRequest

from .malformed_input_data import MalformedInputData
from .session import Session


class AnswerCompanyWorkInviteForm(Protocol):
    def get_invite_id_field(self) -> str:
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
        if self.session.get_current_user():
            return AnswerCompanyWorkInviteRequest(True, invite_id, uuid4())
        else:
            return None
