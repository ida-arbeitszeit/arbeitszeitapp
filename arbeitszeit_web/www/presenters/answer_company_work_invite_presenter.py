from dataclasses import dataclass

from arbeitszeit.interactors.answer_company_work_invite import (
    AnswerCompanyWorkInviteResponse,
)
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class AnswerCompanyWorkInvitePresenter:
    @dataclass
    class ViewModel:
        redirect_url: str

    user_notifier: Notifier
    translator: Translator
    url_index: UrlIndex

    def present(self, response: AnswerCompanyWorkInviteResponse) -> ViewModel:
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
        return self.ViewModel(redirect_url=self.url_index.get_member_dashboard_url())
