from arbeitszeit.use_cases.confirm_company import ConfirmCompanyUseCase as UseCase

from .base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(UseCase)

    def test_using_empty_string_as_email_address_does_not_confirm_company(self) -> None:
        response = self.use_case.confirm_company(
            request=UseCase.Request(email_address="")
        )
        assert not response.is_confirmed

    def test_can_confirm_previously_registered_company(self) -> None:
        expected_email_address = "test@cp.org"
        company = self.company_generator.create_company(
            confirmed=False, email=expected_email_address
        )
        response = self.use_case.confirm_company(
            request=UseCase.Request(email_address=expected_email_address)
        )
        assert response.is_confirmed
        assert response.user_id == company

    def test_cannot_confirm_company_twice(
        self,
    ) -> None:
        expected_email_address = "test@cp.org"
        self.company_generator.create_company(
            confirmed=False, email=expected_email_address
        )
        request = UseCase.Request(email_address=expected_email_address)
        self.use_case.confirm_company(request=request)
        response = self.use_case.confirm_company(request=request)
        assert not response.is_confirmed
