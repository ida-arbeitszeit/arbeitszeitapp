from arbeitszeit_web.www.controllers.review_registered_consumptions_controller import (
    InvalidRequest,
    ReviewRegisteredConsumptionsController,
)
from tests.www.base_test_case import BaseTestCase


class ReviewRegisteredConsumptionsControllerTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.controller = self.injector.get(ReviewRegisteredConsumptionsController)

    def test_401_is_returned_if_no_user_is_logged_in(self):
        request = self.controller.create_use_case_request()
        assert isinstance(request, InvalidRequest)
        assert request.status_code == 401

    def test_403_is_returned_if_user_is_a_member(self):
        self.session.login_member(self.member_generator.create_member())
        request = self.controller.create_use_case_request()
        assert isinstance(request, InvalidRequest)
        assert request.status_code == 403

    def test_403_is_returned_if_user_is_an_accountant(self):
        self.session.login_accountant(self.accountant_generator.create_accountant())
        request = self.controller.create_use_case_request()
        assert isinstance(request, InvalidRequest)
        assert request.status_code == 403

    def test_use_case_request_contains_currently_logged_in_company_id(self):
        expected_company_id = self.company_generator.create_company()
        self.session.login_company(expected_company_id)
        request = self.controller.create_use_case_request()
        assert request.providing_company == expected_company_id
