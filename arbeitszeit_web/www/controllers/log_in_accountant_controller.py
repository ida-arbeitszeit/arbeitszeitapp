from arbeitszeit.interactors.log_in_accountant import (
    LogInAccountantInteractor as Interactor,
)
from arbeitszeit_web.forms import LogInAccountantForm


class LogInAccountantController:
    def process_login_form(self, login_form: LogInAccountantForm) -> Interactor.Request:
        return Interactor.Request(
            email_address=login_form.email_field().get_value(),
            password=login_form.password_field().get_value(),
        )
