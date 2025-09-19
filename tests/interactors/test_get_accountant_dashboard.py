from uuid import uuid4

from arbeitszeit.interactors.get_accountant_dashboard import (
    GetAccountantDashboardInteractor,
)
from tests.interactors.base_test_case import BaseTestCase


class InteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(GetAccountantDashboardInteractor)

    def test_retrieving_dashboard_for_nonexisting_accountant_fails(self):
        with self.assertRaises(self.interactor.Failure):
            self.interactor.get_dashboard(uuid4())

    def test_retrieving_dashboard_for_existing_accountant_succeeds(self):
        accountant = self.accountant_generator.create_accountant()
        response = self.interactor.get_dashboard(accountant)
        assert isinstance(response, self.interactor.Response)

    def test_retrieved_dashboard_has_correct_id(self):
        expected_accountant = self.accountant_generator.create_accountant()
        response = self.interactor.get_dashboard(expected_accountant)
        self.assertEqual(response.accountant_id, expected_accountant)

    def test_retrieved_dashboard_has_correct_accountant_name(self):
        expected_name = "test acc name"
        expected_accountant = self.accountant_generator.create_accountant(
            name=expected_name
        )
        response = self.interactor.get_dashboard(expected_accountant)
        self.assertEqual(response.name, expected_name)

    def test_retrieved_dashboard_has_an_accountant_email(self):
        expected_email = "testmail@cp.org"
        expected_accountant = self.accountant_generator.create_accountant(
            email_address=expected_email
        )
        response = self.interactor.get_dashboard(expected_accountant)
        self.assertEqual(response.email, expected_email)
