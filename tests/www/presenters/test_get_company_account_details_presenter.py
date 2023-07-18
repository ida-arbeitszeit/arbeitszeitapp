from uuid import uuid4

from arbeitszeit.use_cases import get_user_account_details as use_case
from arbeitszeit_web.www.presenters.get_company_account_details_presenter import (
    GetCompanyAccountDetailsPresenter,
)

from .base_test_case import BaseTestCase


class GetCompanyAccountDetailsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetCompanyAccountDetailsPresenter)

    def test_that_email_address_from_response_is_rendered_as_is(self) -> None:
        expected_email_address = "test@test.test"
        response = use_case.Response(
            user_info=use_case.UserInfo(
                id=uuid4(), email_address=expected_email_address
            )
        )
        view_model = self.presenter.render_company_account_details(response)
        assert view_model.email_address == expected_email_address

    def test_that_user_id_is_rendered_as_string(self) -> None:
        user_id = uuid4()
        response = use_case.Response(
            user_info=use_case.UserInfo(id=user_id, email_address="test@test.test")
        )
        view_model = self.presenter.render_company_account_details(response)
        assert view_model.user_id == str(user_id)
