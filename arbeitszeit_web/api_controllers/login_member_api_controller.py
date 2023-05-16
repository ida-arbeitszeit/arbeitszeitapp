from typing import List

from arbeitszeit.use_cases.log_in_member import LogInMemberUseCase
from arbeitszeit_web.api_controllers.expected_input import ExpectedInput
from arbeitszeit_web.api_presenters.response_errors import Unauthorized
from arbeitszeit_web.request import Request


class LoginMemberApiController:
    @classmethod
    def create_expected_inputs(cls) -> List[ExpectedInput]:
        return [
            ExpectedInput(
                name="email",
                type=str,
                description="Email.",
                default=None,
            ),
            ExpectedInput(
                name="password",
                type=str,
                description="Password.",
                default=None,
            ),
        ]

    def create_request(self, request: Request) -> LogInMemberUseCase.Request:
        email = request.get_form("email")
        password = request.get_form("password")
        if not email or not password:
            raise Unauthorized(message="Email or password missing.")
        return LogInMemberUseCase.Request(email=email, password=password)
