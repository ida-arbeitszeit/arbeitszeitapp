from dataclasses import dataclass

from arbeitszeit.use_cases import (
    CheckForUnreadMessagesRequest,
    CheckForUnreadMessagesResponse,
)

from .session import Session


@dataclass
class ViewModel:
    show_unread_messages_indicator: bool


class CheckForUnreadMessagesPresenter:
    def present(self, response: CheckForUnreadMessagesResponse) -> ViewModel:
        return ViewModel(show_unread_messages_indicator=response.has_unread_messages)

    def anonymous_view_model(self) -> ViewModel:
        return ViewModel(show_unread_messages_indicator=False)


@dataclass
class CheckForUnreadMessagesController:
    session: Session

    def create_use_case_request(self) -> CheckForUnreadMessagesRequest:
        user_id = self.session.get_current_user()
        if user_id is None:
            raise ValueError("User is not authenticated")
        return CheckForUnreadMessagesRequest(user=user_id)
