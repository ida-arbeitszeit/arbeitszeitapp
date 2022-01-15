from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.use_cases import (
    CheckForUnreadMessagesRequest,
    CheckForUnreadMessagesResponse,
)


@dataclass
class ViewModel:
    show_unread_messages_indicator: bool


class CheckForUnreadMessagesPresenter:
    def present(self, response: CheckForUnreadMessagesResponse) -> ViewModel:
        return ViewModel(show_unread_messages_indicator=response.has_unread_messages)

    def anonymous_view_model(self) -> ViewModel:
        return ViewModel(show_unread_messages_indicator=False)


class CheckForUnreadMessagesController:
    def create_use_case_request(self, user_id: UUID) -> CheckForUnreadMessagesRequest:
        return CheckForUnreadMessagesRequest(user=user_id)
