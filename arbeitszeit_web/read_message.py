from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.use_cases import ReadMessageRequest, ReadMessageSuccess

from .session import Session


@dataclass
class ReadMessageController:
    session: Session

    def process_request_data(self, message_id: UUID) -> ReadMessageRequest:
        user_id = self.session.get_current_user()
        if user_id is None:
            raise ValueError("User is not authenticated")
        return ReadMessageRequest(
            reader_id=user_id,
            message_id=message_id,
        )


@dataclass
class ViewModel:
    title: str
    content: str


class ReadMessagePresenter:
    def present(self, use_case_response: ReadMessageSuccess) -> ViewModel:
        return ViewModel(
            title=use_case_response.message_title,
            content=use_case_response.message_content,
        )
