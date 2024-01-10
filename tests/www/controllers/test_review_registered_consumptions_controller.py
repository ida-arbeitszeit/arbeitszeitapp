from arbeitszeit_web.www.controllers.review_registered_consumptions_controller import (
    ReviewRegisteredConsumptionsController,
)
from tests.www.base_test_case import BaseTestCase


class ReviewRegisteredConsumptionsControllerTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.controller = self.injector.get(ReviewRegisteredConsumptionsController)

    def test_none_is_returned_if_no_user_is_logged_in(self):
        self.assertIsNone(self.controller.create_use_case_request())

    def test_none_is_returned_if_user_is_a_member(self):
        self.session.login_member(self.member_generator.create_member())
        self.assertIsNone(self.controller.create_use_case_request())

    def test_none_is_returned_if_user_is_an_accountant(self):
        self.session.login_accountant(self.accountant_generator.create_accountant())
        self.assertIsNone(self.controller.create_use_case_request())

    def test_use_case_request_is_created_if_user_is_a_company(self):
        self.session.login_company(self.company_generator.create_company())
        self.assertIsNotNone(self.controller.create_use_case_request())

    def test_use_case_request_contains_providing_company(self):
        company = self.company_generator.create_company()
        self.session.login_company(company)
        request = self.controller.create_use_case_request()
        self.assertEqual(request.providing_company, company)
