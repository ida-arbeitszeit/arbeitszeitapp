from arbeitszeit.interactors.register_company import RegisterCompany
from arbeitszeit_web.forms import RegisterForm


class RegisterCompanyController:
    def create_request(
        self,
        form: RegisterForm,
    ) -> RegisterCompany.Request:
        return RegisterCompany.Request(
            email=form.email_field.get_value(),
            name=form.name_field.get_value(),
            password=form.password_field.get_value(),
        )
