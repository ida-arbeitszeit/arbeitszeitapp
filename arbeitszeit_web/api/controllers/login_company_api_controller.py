from arbeitszeit.interactors.log_in_company import LogInCompanyInteractor
from arbeitszeit_web.api.controllers.parameters import BodyParameter
from arbeitszeit_web.api.response_errors import BadRequest
from arbeitszeit_web.request import Request

login_company_expected_inputs = [
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


class LoginCompanyApiController:
    def create_request(self, request: Request) -> LogInCompanyInteractor.Request:
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
        return LogInCompanyInteractor.Request(email_address=email, password=password)
