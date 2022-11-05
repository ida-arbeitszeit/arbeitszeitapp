from uuid import uuid4

from arbeitszeit.use_cases.get_accountant_dashboard import GetAccountantDashboardUseCase
from tests.data_generators import AccountantGenerator
from tests.use_cases.base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(GetAccountantDashboardUseCase)
        self.accountant_generator = self.injector.get(AccountantGenerator)

    def test_retrieving_dashboard_for_nonexisting_accountant_fails(self):
        with self.assertRaises(self.use_case.Failure):
            self.use_case.get_dashboard(uuid4())

    def test_retrieving_dashboard_for_existing_accountant_succeeds(self):
        accountant = self.accountant_generator.create_accountant()
        response = self.use_case.get_dashboard(accountant)
        assert isinstance(response, self.use_case.Response)

    def test_retrieved_dashboard_has_correct_id(self):
        expected_accountant = self.accountant_generator.create_accountant()
        response = self.use_case.get_dashboard(expected_accountant)
        self.assertEqual(response.accountant_id, expected_accountant)

    def test_retrieved_dashboard_has_correct_accountant_name(self):
        expected_name = "test acc name"
        expected_accountant = self.accountant_generator.create_accountant(
            name=expected_name
        )
        response = self.use_case.get_dashboard(expected_accountant)
        self.assertEqual(response.name, expected_name)

    def test_retrieved_dashboard_has_an_accountant_email(self):
        expected_email = "testmail@cp.org"
        expected_accountant = self.accountant_generator.create_accountant(
            email_address=expected_email
        )
        response = self.use_case.get_dashboard(expected_accountant)
        self.assertEqual(response.email, expected_email)
