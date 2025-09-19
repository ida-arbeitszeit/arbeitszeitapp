from dataclasses import dataclass

from arbeitszeit.interactors.log_in_company import LogInCompanyInteractor
from arbeitszeit_web.api.presenters.interfaces import JsonBoolean, JsonObject, JsonValue
from arbeitszeit_web.api.response_errors import Unauthorized
from arbeitszeit_web.session import Session


@dataclass
class LoginCompanyApiPresenter:
    @dataclass
    class ViewModel:
        success: bool

    @classmethod
    def get_schema(cls) -> JsonValue:
        return JsonObject(
            members=dict(success=JsonBoolean()),
            name="LoginCompanyResponse",
        )

    session: Session

    def create_view_model(self, response: LogInCompanyInteractor.Response) -> ViewModel:
        if response.is_logged_in:
            assert response.user_id
            self.session.login_company(company=response.user_id, remember=False)
            return self.ViewModel(success=True)
        else:
            if (
                response.rejection_reason
                == LogInCompanyInteractor.RejectionReason.invalid_email_address
            ):
                raise Unauthorized(message="Unknown email address.")
            else:
                raise Unauthorized(message="Invalid password.")
