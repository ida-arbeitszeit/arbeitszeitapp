from dataclasses import dataclass
from typing import Optional

from arbeitszeit.use_cases import request_email_address_change as use_case
from arbeitszeit_web.forms import RequestEmailAddressChangeForm
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class ViewModel:
    redirect_url: Optional[str]


@dataclass
class RequestEmailAddressChangePresenter:
    url_index: UrlIndex
    session: Session
    notifier: Notifier
    translator: Translator

    def render_response(
        self, uc_response: use_case.Response, form: RequestEmailAddressChangeForm
    ) -> ViewModel:
        redirect_url: Optional[str]
        if uc_response.is_rejected:
            if (
                uc_response.rejection_reason
                == use_case.Response.RejectionReason.invalid_email_address
            ):
                form.new_email_field.attach_error(
                    self.translator.gettext("The email address seems to be invalid.")
                )
            elif (
                uc_response.rejection_reason
                == use_case.Response.RejectionReason.current_email_address_does_not_exist
            ):
                pass
            elif (
                uc_response.rejection_reason
                == use_case.Response.RejectionReason.new_email_address_already_taken
            ):
                form.new_email_field.attach_error(
                    self.translator.gettext(
                        "The email address seems to be already taken."
                    )
                )
            elif (
                uc_response.rejection_reason
                == use_case.Response.RejectionReason.incorrect_password
            ):
                form.current_password_field.attach_error(
                    self.translator.gettext("The password is incorrect.")
                )
            redirect_url = None
            self.notifier.display_warning(
                self.translator.gettext(
                    "Your request for an email address change was rejected."
                )
            )
        else:
            self.notifier.display_info(
                self.translator.gettext(
                    "A confirmation mail has been sent to your new email address."
                )
            )
            redirect_url = self.url_index.get_user_account_details_url()
        return ViewModel(redirect_url=redirect_url)
