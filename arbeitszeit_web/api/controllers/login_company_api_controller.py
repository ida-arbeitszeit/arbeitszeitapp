from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases.log_in_company import LogInCompanyUseCase
from arbeitszeit_web.api.controllers.expected_input import ExpectedInput, InputLocation
from arbeitszeit_web.api.response_errors import BadRequest
from arbeitszeit_web.request import Request


@dataclass
class LoginCompanyApiController:
    @classmethod
    def create_expected_inputs(cls) -> List[ExpectedInput]:
        return [
            ExpectedInput(
                name="email",
                type=str,
                description="Email.",
                default=None,
                location=InputLocation.form,
                required=True,
            ),
            ExpectedInput(
                name="password",
                type=str,
                description="Password.",
                default=None,
                location=InputLocation.form,
                required=True,
            ),
        ]

    request: Request

    def create_request(self) -> LogInCompanyUseCase.Request:
        email = self.request.get_form("email")
        password = self.request.get_form("password")
        if not email:
            raise BadRequest(message="Email missing.")
        if not password:
            raise BadRequest(message="Password missing.")
        return LogInCompanyUseCase.Request(email_address=email, password=password)
