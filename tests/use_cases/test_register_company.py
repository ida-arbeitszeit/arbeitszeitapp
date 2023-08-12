from uuid import UUID

from arbeitszeit.use_cases.confirm_member import ConfirmMemberUseCase
from arbeitszeit.use_cases.get_company_dashboard import GetCompanyDashboardUseCase
from arbeitszeit.use_cases.register_company import RegisterCompany
from tests.token import TokenDeliveryService

from .base_test_case import BaseTestCase


class RegisterCompanyTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(RegisterCompany)
        self.token_delivery = self.injector.get(TokenDeliveryService)
        self.get_company_dashboard_use_case = self.injector.get(
            GetCompanyDashboardUseCase
        )
        self.confirm_member_use_case = self.injector.get(ConfirmMemberUseCase)

    def test_that_a_token_is_sent_out_when_a_company_registers(self) -> None:
        self.use_case.register_company(self._create_request())
        self.assertTrue(self.token_delivery.presented_company_tokens)

    def test_registration_message_was_delivered_to_user(self) -> None:
        expected_mail = "mailtest321@cp.org"
        self.use_case.register_company(self._create_request(email=expected_mail))
        self._assert_company_received_registration_message(expected_mail)

    def test_that_registering_company_is_possible(self) -> None:
        response = self.use_case.register_company(self._create_request())
        self.assertFalse(response.is_rejected)

    def test_that_correct_error_is_raised_when_user_with_mail_exists(self) -> None:
        self.company_generator.create_company_record(email="test@cp.org")
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

    def test_that_company_registration_with_preexisting_member_email_address_is_rejected_when_provided_password_does_not_match_member_password(
        self,
    ) -> None:
        email_address = "test@test.test"
        self.member_generator.create_member(
            email=email_address, password="member password"
        )
        request = self._create_request(email=email_address, password="company password")
        response = self.use_case.register_company(request)
        assert response.is_rejected

    def test_that_company_registration_succeeds_with_preexisting_member_email_address_when_provided_password_matches_member_password(
        self,
    ) -> None:
        email_address = "test@test.test"
        password = "matching password"
        self.member_generator.create_member(
            email=email_address,
            password=password,
        )
        request = self._create_request(email=email_address, password=password)
        response = self.use_case.register_company(request)
        assert not response.is_rejected

    def test_when_provided_password_does_not_match_preexisting_member_password_then_proper_rejection_reason_is_given(
        self,
    ) -> None:
        email_address = "test@test.test"
        self.member_generator.create_member(
            email=email_address, password="member password"
        )
        request = self._create_request(email=email_address, password="company password")
        response = self.use_case.register_company(request)
        assert (
            response.rejection_reason
            == RegisterCompany.Response.RejectionReason.user_password_is_invalid
        )

    def test_that_creating_a_company_with_same_email_as_member_does_not_require_confirmation_of_member_email_again(
        self,
    ) -> None:
        email_address = "test@test.test"
        password = "matching password"
        self.member_generator.create_member(
            email=email_address,
            password=password,
        )
        request = self._create_request(email=email_address, password=password)
        self.use_case.register_company(request)
        response = self.confirm_member_use_case.confirm_member(
            ConfirmMemberUseCase.Request(email_address=email_address)
        )
        assert not response.is_confirmed

    def _create_request(
        self,
        *,
        email: str = "test@cp.org",
        name: str = "test name",
        password: str = "test password",
    ) -> RegisterCompany.Request:
        return RegisterCompany.Request(
            email=email,
            name=name,
            password=password,
        )

    def _get_company_info(
        self, company: UUID
    ) -> GetCompanyDashboardUseCase.Response.CompanyInfo:
        response = self.get_company_dashboard_use_case.get_dashboard(company)
        return response.company_info

    def _assert_company_received_registration_message(self, email: str) -> None:
        for token in self.token_delivery.presented_company_tokens:
            if token.email_address == email:
                break
        else:
            assert False, "Token was not delivered to registering user"
