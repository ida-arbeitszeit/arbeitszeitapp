from flask_restx import Namespace, Resource

from arbeitszeit.use_cases.log_in_company import LogInCompanyUseCase
from arbeitszeit.use_cases.log_in_member import LogInMemberUseCase
from arbeitszeit_flask.api.input_documentation import generate_input_documentation
from arbeitszeit_flask.api.response_handling import error_response_handling
from arbeitszeit_flask.api.schema_converter import SchemaConverter
from arbeitszeit_flask.dependency_injection import with_injection
from arbeitszeit_web.api.controllers.login_company_api_controller import (
    LoginCompanyApiController,
)
from arbeitszeit_web.api.controllers.login_member_api_controller import (
    LoginMemberApiController,
)
from arbeitszeit_web.api.presenters.login_company_api_presenter import (
    LoginCompanyApiPresenter,
)
from arbeitszeit_web.api.presenters.login_member_api_presenter import (
    LoginMemberApiPresenter,
)
from arbeitszeit_web.api.response_errors import BadRequest, Unauthorized

namespace = Namespace("auth", "Authentification related endpoints.")

login_member_input_documentation = generate_input_documentation(
    LoginMemberApiController.create_expected_inputs()
)

login_member_model = SchemaConverter(namespace).json_schema_to_flaskx(
    schema=LoginMemberApiPresenter.get_schema()
)


@namespace.route("/login_member")
class LoginMember(Resource):
    @namespace.expect(login_member_input_documentation)
    @namespace.marshal_with(login_member_model, skip_none=True)
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


login_company_input_documentation = generate_input_documentation(
    LoginCompanyApiController.create_expected_inputs()
)

login_company_model = SchemaConverter(namespace).json_schema_to_flaskx(
    schema=LoginCompanyApiPresenter.get_schema()
)


@namespace.route("/login_company")
class LoginCompany(Resource):
    @namespace.expect(login_company_input_documentation)
    @namespace.marshal_with(login_company_model, skip_none=True)
    @error_response_handling(
        error_responses=[Unauthorized, BadRequest], namespace=namespace
    )
    @with_injection()
    def post(
        self,
        controller: LoginCompanyApiController,
        login_company: LogInCompanyUseCase,
        presenter: LoginCompanyApiPresenter,
    ):
        """
        Login with a company account.
        """
        use_case_request = controller.create_request()
        response = login_company.log_in_company(use_case_request)
        view_model = presenter.create_view_model(response)
        return view_model
