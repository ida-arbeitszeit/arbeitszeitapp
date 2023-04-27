from unittest import TestCase
from uuid import UUID

from arbeitszeit.use_cases.get_company_dashboard import GetCompanyDashboardUseCase
from arbeitszeit.use_cases.register_company import RegisterCompany
from tests.data_generators import CompanyGenerator
from tests.token import TokenDeliveryService

from .dependency_injection import get_dependency_injector


class RegisterCompanyTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(RegisterCompany)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.token_delivery = self.injector.get(TokenDeliveryService)
        self.get_company_dashboard_use_case = self.injector.get(
            GetCompanyDashboardUseCase
        )

    def test_that_a_token_is_sent_out_when_a_company_registers(self) -> None:
        self.use_case.register_company(self._create_request())
        self.assertTrue(self.token_delivery.presented_company_tokens)

    def test_registration_message_was_delivered_to_user(self) -> None:
        expected_mail = "mailtest321@cp.org"
        response = self.use_case.register_company(
            self._create_request(email=expected_mail)
        )
        assert response.company_id
        self._assert_company_received_registration_message(response.company_id)

    def test_that_registering_company_is_possible(self) -> None:
        response = self.use_case.register_company(self._create_request())
        self.assertFalse(response.is_rejected)

    def test_that_correct_error_is_raised_when_user_with_mail_exists(self) -> None:
        self.company_generator.create_company_entity(email="test@cp.org")
        response = self.use_case.register_company(
            self._create_request(email="test@cp.org")
        )
        assert response.is_rejected
        assert (
            response.rejection_reason
            == RegisterCompany.Response.RejectionReason.company_already_exists
        )

    def test_company_is_registered_with_correct_email_and_name(self) -> None:
        expected_name = "test name 123"
        expected_email = "expected@email.test"
        request = self._create_request(email=expected_email, name=expected_name)
        response = self.use_case.register_company(request)
        assert response.company_id
        company_info = self._get_company_info(response.company_id)
        assert company_info.name == expected_name
        assert company_info.email == expected_email

    def _create_request(
        self, *, email: str = "test@cp.org", name: str = "test name"
    ) -> RegisterCompany.Request:
        return RegisterCompany.Request(
            email=email,
            name=name,
            password="super safe",
        )

    def _get_company_info(
        self, company: UUID
    ) -> GetCompanyDashboardUseCase.Response.CompanyInfo:
        response = self.get_company_dashboard_use_case.get_dashboard(company)
        return response.company_info

    def _assert_company_received_registration_message(self, company: UUID) -> None:
        for token in self.token_delivery.presented_company_tokens:
            if token.user == company:
                break
        else:
            assert False, "Token was not delivered to registering user"
