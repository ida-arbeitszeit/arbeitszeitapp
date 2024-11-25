from dataclasses import dataclass

from arbeitszeit.use_cases.log_in_member import LogInMemberUseCase
from arbeitszeit_web.api.controllers.parameters import BodyParameter
from arbeitszeit_web.api.response_errors import BadRequest
from arbeitszeit_web.request import Request

login_member_expected_inputs = [
    BodyParameter(
        name="email",
        type=str,
        description="Email.",
        default=None,
        required=True,
    ),
    BodyParameter(
        name="password",
        type=str,
        description="Password.",
        default=None,
        required=True,
    ),
]


@dataclass
class LoginMemberApiController:
    def create_request(self, request: Request) -> LogInMemberUseCase.Request:
        json_body = request.get_json()
        if not isinstance(json_body, dict):
            raise BadRequest("Email missing.")
        email = json_body.get("email")
        password = json_body.get("password")
        if not email:
            raise BadRequest(message="Email missing.")
        if not password:
            raise BadRequest(message="Password missing.")
        assert isinstance(email, str)
        assert isinstance(password, str)
        return LogInMemberUseCase.Request(email=email, password=password)
