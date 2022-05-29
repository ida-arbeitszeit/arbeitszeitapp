from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.use_cases import ListMessages
from arbeitszeit_web.translator import Translator

from .session import Session
from .url_index import WorkInviteMessageUrlIndex


@dataclass
class ListMessagesController:
    session: Session

    def process_request_data(self) -> Optional[ListMessages.Request]:
        current_user = self.session.get_current_user()
        if current_user is None:
            return None
        return ListMessages.Request(user=current_user)


@dataclass
class ListMessagesPresenter:
    @dataclass
    class WorkerInviteMessage:
        title: str
        show_unread_message_indicator: bool
        url: str
        creation_date: str

    @dataclass
    class ViewModel:
        worker_invite_messages: List[ListMessagesPresenter.WorkerInviteMessage]

    url_index: WorkInviteMessageUrlIndex
    datetime_service: DatetimeService
    translator: Translator

    def present(self, use_case_response: ListMessages.Response) -> ViewModel:
        return self.ViewModel(
            worker_invite_messages=[
                self.WorkerInviteMessage(
                    title=self.translator.gettext(
                        "Invitation from %(name)s to join its company"
                    )
                    % dict(name=m.company_name),
                    show_unread_message_indicator=not m.is_read,
                    url=self.url_index.get_work_invite_message_url(m.message_id),
                    creation_date=self.datetime_service.format_datetime(
                        m.creation_date, zone="Europe/Berlin", fmt="%d.%m."
                    ),
                )
                for m in use_case_response.worker_invite_messages
            ]
        )
