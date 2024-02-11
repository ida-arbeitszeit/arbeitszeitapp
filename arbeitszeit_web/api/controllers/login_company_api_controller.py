from dataclasses import dataclass

from arbeitszeit.use_cases.log_in_company import LogInCompanyUseCase
from arbeitszeit_web.api.controllers.parameters import FormParameter
from arbeitszeit_web.api.response_errors import BadRequest
from arbeitszeit_web.request import Request

login_company_expected_inputs = [
    FormParameter(
        name="email",
        type=str,
        description="Email.",
        default=None,
        required=True,
    ),
    FormParameter(
        name="password",
        type=str,
        description="Password.",
        default=None,
        required=True,
    ),
]


@dataclass
class LoginCompanyApiController:
    request: Request

    def create_request(self) -> LogInCompanyUseCase.Request:
        email = self.request.get_form("email")
        password = self.request.get_form("password")
        if not email:
            raise BadRequest(message="Email missing.")
        if not password:
            raise BadRequest(message="Password missing.")
        return LogInCompanyUseCase.Request(email_address=email, password=password)
