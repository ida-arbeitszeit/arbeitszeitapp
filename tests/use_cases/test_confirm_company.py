from datetime import datetime

from arbeitszeit.use_cases.confirm_company import ConfirmCompanyUseCase as UseCase
from tests.token import FakeTokenService, TokenDeliveryService
from tests.use_cases.repositories import CompanyRepository

from .base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(UseCase)
        self.token_service = self.injector.get(FakeTokenService)
        self.token_deliverer = self.injector.get(TokenDeliveryService)
        self.company_repository = self.injector.get(CompanyRepository)

    def test_using_empty_string_as_token_does_not_confirm_company(self) -> None:
        response = self.use_case.confirm_company(request=UseCase.Request(token=""))
        assert not response.is_confirmed

    def test_using_a_token_delivered_on_registration_does_confirm_company(self) -> None:
        self.company_generator.create_company(confirmed=False)
        token = self.token_deliverer.presented_company_tokens[-1].token
        response = self.use_case.confirm_company(request=UseCase.Request(token=token))
        assert response.is_confirmed

    def test_using_delivered_token_confirms_company_that_token_was_delivered_to(
        self,
    ) -> None:
        self.company_generator.create_company(confirmed=False)
        token = self.token_deliverer.presented_company_tokens[-1].token
        company = self.token_deliverer.presented_company_tokens[-1].user
        response = self.use_case.confirm_company(request=UseCase.Request(token=token))
        assert response.user_id == company

    def test_cannot_confirm_company_twice(
        self,
    ) -> None:
        self.company_generator.create_company(confirmed=False)
        token = self.token_deliverer.presented_company_tokens[-1].token
        self.use_case.confirm_company(request=UseCase.Request(token=token))
        response = self.use_case.confirm_company(request=UseCase.Request(token=token))
        assert not response.is_confirmed

    def test_that_confirmation_date_is_set_correctly(
        self,
    ) -> None:
        expected_confirmation_timestamp = datetime(2000, 2, 1)
        self.datetime_service.freeze_time(expected_confirmation_timestamp)
        self.company_generator.create_company(confirmed=False)
        token = self.token_deliverer.presented_company_tokens[-1].token
        company = self.token_deliverer.presented_company_tokens[-1].user
        self.use_case.confirm_company(request=UseCase.Request(token=token))
        company_entity = (
            self.company_repository.get_companies().with_id(company).first()
        )
        assert company_entity
        assert company_entity.confirmed_on == expected_confirmation_timestamp
