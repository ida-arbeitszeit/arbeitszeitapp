from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.use_cases import ReadMessageRequest, ReadMessageSuccess

from .session import Session
from .user_action_resolver import UserActionResolver


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
    show_action_link: bool
    action_link_reference: str
    action_link_label: str


@dataclass
class ReadMessagePresenter:
    action_link_resolver: UserActionResolver

    def present(self, use_case_response: ReadMessageSuccess) -> ViewModel:
        print(use_case_response)
        action_link_reference: str
        action_link_label: str
        if use_case_response.user_action is None:
            action_link_reference = ""
            action_link_label = ""
        else:
            action_link_reference = (
                self.action_link_resolver.resolve_user_action_reference(
                    use_case_response.user_action
                )
            )
            action_link_label = self.action_link_resolver.resolve_user_action_name(
                use_case_response.user_action
            )
        return ViewModel(
            title=use_case_response.message_title,
            content=use_case_response.message_content,
            show_action_link=use_case_response.user_action is not None,
            action_link_reference=action_link_reference,
            action_link_label=action_link_label,
        )
