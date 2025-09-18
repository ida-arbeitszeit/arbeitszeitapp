from dataclasses import dataclass

from arbeitszeit.interactors import resend_work_invite
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.translator import Translator


@dataclass
class ViewModel:
    status_code: int


@dataclass
class ResendWorkInvitePresenter:
    notifier: Notifier
    translator: Translator

    def present(self, response: resend_work_invite.Response) -> ViewModel:
        match response.rejection_reason:
            case resend_work_invite.Response.RejectionReason.INVITE_DOES_NOT_EXIST:
                self.notifier.display_warning(
                    self.translator.gettext("Invite does not exist.")
                )
                return ViewModel(status_code=400)
            case None:
                self.notifier.display_info(
                    self.translator.gettext("Invite has been resent successfully.")
                )
                return ViewModel(status_code=302)
