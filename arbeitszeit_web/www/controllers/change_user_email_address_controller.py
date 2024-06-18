from dataclasses import dataclass
from datetime import timedelta

from arbeitszeit.use_cases import change_user_email_address
from arbeitszeit_web.forms import ConfirmEmailAddressChangeForm
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.session import Session
from arbeitszeit_web.token import TokenService
from arbeitszeit_web.translator import Translator


@dataclass
class ChangeUserEmailAddressController:
    token_service: TokenService
    session: Session
    notifier: Notifier
    translator: Translator

    def create_use_case_request(
        self, new_email_address: str, form: ConfirmEmailAddressChangeForm
    ) -> change_user_email_address.Request | None:
        current_user = self.session.get_current_user()
        if current_user is None:
            return None
        if not form.is_accepted_field().get_value():
            self.notifier.display_info(
                self.translator.gettext("Email address remains unchanged.")
            )
            return None
        return change_user_email_address.Request(
            user=current_user,
            new_email=new_email_address,
        )

    def extract_email_addresses_from_token(self, token: str) -> tuple[str, str] | None:
        unpacked_token = self.token_service.confirm_token(token, timedelta(minutes=15))
        if unpacked_token is None:
            return None
        if unpacked_token.count(":") != 1:
            return None
        old_email, new_email = unpacked_token.split(":", maxsplit=1)
        if not old_email or not new_email:
            return None
        return old_email, new_email
