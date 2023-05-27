from flask_restx import Namespace, Resource

from arbeitszeit.use_cases.log_in_member import LogInMemberUseCase
from arbeitszeit_flask.api.input_documentation import generate_input_documentation
from arbeitszeit_flask.api.response_handling import error_response_handling
from arbeitszeit_flask.api.schema_converter import SchemaConverter
from arbeitszeit_flask.dependency_injection import with_injection
from arbeitszeit_web.api_controllers.login_member_api_controller import (
    LoginMemberApiController,
)
from arbeitszeit_web.api_presenters.login_member_api_presenter import (
    LoginMemberApiPresenter,
)
from arbeitszeit_web.api_presenters.response_errors import BadRequest, Unauthorized

namespace = Namespace("auth", "Authentification related endpoints.")

input_documentation = generate_input_documentation(
    LoginMemberApiController.create_expected_inputs()
)

model = SchemaConverter(namespace).json_schema_to_flaskx(
    schema=LoginMemberApiPresenter.get_schema()
)


@namespace.route("/login_member")
class LoginMember(Resource):
    @namespace.expect(input_documentation)
    @namespace.marshal_with(model)
    @error_response_handling(
        error_responses=[Unauthorized, BadRequest], namespace=namespace
    )
    @with_injection()
    def post(
        self,
        controller: LoginMemberApiController,
        login_member: LogInMemberUseCase,
        presenter: LoginMemberApiPresenter,
    ):
        """
        Login with a member account.
        """
        use_case_request = controller.create_request()
        response = login_member.log_in_member(use_case_request)
        view_model = presenter.create_view_model(response)
        return view_model
