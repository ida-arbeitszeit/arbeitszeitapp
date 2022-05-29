from dataclasses import dataclass
from typing import Protocol, Union
from uuid import UUID

from arbeitszeit.use_cases import AnswerCompanyWorkInvite

from .malformed_input_data import MalformedInputData
from .notification import Notifier
from .session import Session
from .translator import Translator
from .url_index import ListMessagesUrlIndex


class AnswerCompanyWorkInviteForm(Protocol):
    def get_is_accepted_field(self) -> bool:
        ...


@dataclass(frozen=True)
class AnswerCompanyWorkInviteController:
    session: Session

    def import_form_data(
        self, form: AnswerCompanyWorkInviteForm, invite_id: UUID
    ) -> Union[None, MalformedInputData, AnswerCompanyWorkInvite.Request]:
        requesting_user = self.session.get_current_user()
        if requesting_user is not None:
            return AnswerCompanyWorkInvite.Request(
                form.get_is_accepted_field(), invite_id, requesting_user
            )
        else:
            return None


@dataclass
class AnswerCompanyWorkInvitePresenter:
    @dataclass
    class ViewModel:
        redirect_url: str

    user_notifier: Notifier
    url_index: ListMessagesUrlIndex
    translator: Translator

    def present(self, response: AnswerCompanyWorkInvite.Response) -> ViewModel:
        if response.is_success:
            if response.is_accepted:
                self.user_notifier.display_info(
                    self.translator.gettext('You successfully joined "%(company)s".')
                    % dict(company=response.company_name)
                )
            else:
                self.user_notifier.display_info(
                    self.translator.gettext(
                        'You rejected the invitation from "%(company)s".'
                    )
                    % dict(company=response.company_name)
                )
        else:
            self.user_notifier.display_warning(
                self.translator.gettext("Accepting or rejecting is not possible.")
            )
        return self.ViewModel(redirect_url=self.url_index.get_list_messages_url())
