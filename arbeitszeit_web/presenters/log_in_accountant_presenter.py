from dataclasses import dataclass
from typing import Optional

from injector import inject

from arbeitszeit.use_cases.log_in_accountant import LogInAccountantUseCase as UseCase
from arbeitszeit_web.forms import LogInAccountantForm
from arbeitszeit_web.session import Session
from arbeitszeit_web.url_index import UrlIndex


@inject
@dataclass
class LogInAccountantPresenter:
    @dataclass
    class ViewModel:
        redirect_url: Optional[str]

    session: Session
    url_index: UrlIndex

    def present_login_process(
        self, form: LogInAccountantForm, response: UseCase.Response
    ) -> ViewModel:
        if response.user_id is None:
            return self.ViewModel(redirect_url=None)
        self.session.login_accountant(
            email=form.email_field().get_value(),
            remember=form.remember_field().get_value(),
        )
        return self.ViewModel(
            redirect_url=self.session.pop_next_url()
            or self.url_index.get_accountant_dashboard_url()
        )
