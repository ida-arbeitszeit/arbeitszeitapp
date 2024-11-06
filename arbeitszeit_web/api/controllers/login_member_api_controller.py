from dataclasses import dataclass

from arbeitszeit.use_cases.log_in_member import LogInMemberUseCase
from arbeitszeit_web.api.controllers.parameters import FormParameter
from arbeitszeit_web.api.response_errors import BadRequest
from arbeitszeit_web.request import Request

login_member_expected_inputs = [
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
class LoginMemberApiController:
    request: Request

    def create_request(self) -> LogInMemberUseCase.Request:
        email = self.request.get_json("email")
        password = self.request.get_json("password")
        if not email:
            raise BadRequest(message="Email missing.")
        if not password:
            raise BadRequest(message="Password missing.")
        return LogInMemberUseCase.Request(email=email, password=password)
