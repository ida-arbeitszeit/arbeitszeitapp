from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.use_cases import ReadWorkerInviteMessage

from .session import Session


@dataclass
class ReadWorkerInviteMessageController:
    session: Session

    def process_request_data(self, message_id: UUID) -> ReadWorkerInviteMessage.Request:
        user_id = self.session.get_current_user()
        if user_id is None:
            raise ValueError("User is not authenticated")
        return ReadWorkerInviteMessage.Request(
            reader_id=user_id,
            message_id=message_id,
        )


@dataclass
class ViewModel:
    invite_id: str


@dataclass
class ReadWorkerInviteMessagePresenter:
    def present(self, use_case_response: ReadWorkerInviteMessage.Success) -> ViewModel:
        return ViewModel(invite_id=f"{use_case_response.invite_id}")
