from dataclasses import dataclass

from arbeitszeit.use_cases.register_company import RegisterCompany
from arbeitszeit_web.register_company import RegisterForm
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator


@dataclass
class ViewModel:
    is_success_view: bool


@dataclass
class RegisterCompanyPresenter:
    translator: Translator
    session: Session

    def present_company_registration(
        self, response: RegisterCompany.Response, form: RegisterForm
    ) -> ViewModel:
        if response.is_rejected:
            form.add_email_error(
                self.translator.gettext("This email address is already registered.")
            )
            return ViewModel(is_success_view=False)
        assert response.company_id
        self.session.login_company(company=response.company_id)
        return ViewModel(is_success_view=True)
