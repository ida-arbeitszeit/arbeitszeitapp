from arbeitszeit.interactors.confirm_company import (
    ConfirmCompanyInteractor as Interactor,
)

from .base_test_case import BaseTestCase


class InteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(Interactor)

    def test_using_empty_string_as_email_address_does_not_confirm_company(self) -> None:
        response = self.interactor.confirm_company(
            request=Interactor.Request(email_address="")
        )
        assert not response.is_confirmed

    def test_can_confirm_previously_registered_company(self) -> None:
        expected_email_address = "test@cp.org"
        company = self.company_generator.create_company(
            confirmed=False, email=expected_email_address
        )
        response = self.interactor.confirm_company(
            request=Interactor.Request(email_address=expected_email_address)
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
        request = Interactor.Request(email_address=expected_email_address)
        self.interactor.confirm_company(request=request)
        response = self.interactor.confirm_company(request=request)
        assert not response.is_confirmed
