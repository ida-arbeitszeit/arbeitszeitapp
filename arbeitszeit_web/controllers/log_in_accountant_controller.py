from arbeitszeit.use_cases.log_in_accountant import LogInAccountantUseCase as UseCase
from arbeitszeit_web.forms import LogInAccountantForm


class LogInAccountantController:
    def process_login_form(self, login_form: LogInAccountantForm) -> UseCase.Request:
        return UseCase.Request(
            email_address=login_form.email_field().get_value(),
            password=login_form.password_field().get_value(),
        )
