from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from arbeitszeit.use_cases import ListMessagesRequest, ListMessagesResponse

from .session import Session


@dataclass
class ListMessagesController:
    session: Session

    def process_request_data(self) -> Optional[ListMessagesRequest]:
        current_user = self.session.get_current_user()
        if current_user is None:
            return None
        return ListMessagesRequest(user=current_user)


class ListMessagesPresenter:
    def present(self, use_case_response: ListMessagesResponse) -> ViewModel:
        return ViewModel(
            messages=[
                Message(
                    title=m.title,
                    sender_name=m.sender_name,
                    show_unread_message_indicator=not m.is_read,
                )
                for m in use_case_response.messages
            ]
        )


@dataclass
class ViewModel:
    messages: List[Message]


@dataclass
class Message:
    title: str
    sender_name: str
    show_unread_message_indicator: bool
