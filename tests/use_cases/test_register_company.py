from unittest import TestCase

from arbeitszeit.entities import AccountTypes
from arbeitszeit.use_cases import RegisterCompany
from tests.data_generators import CompanyGenerator
from tests.token import TokenDeliveryService

from .dependency_injection import get_dependency_injector
from .repositories import AccountRepository, CompanyRepository

DEFAULT = dict(
    email="test@cp.org",
    name="test name",
    password="super safe",
)


class RegisterCompanyTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(RegisterCompany)
        self.account_repository = self.injector.get(AccountRepository)
        self.company_repo = self.injector.get(CompanyRepository)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.token_delivery = self.injector.get(TokenDeliveryService)

    def test_that_a_token_is_sent_out_when_a_company_registers(self) -> None:
        self.use_case.register_company(RegisterCompany.Request(**DEFAULT))
        self.assertTrue(self.token_delivery.presented_company_tokens)

    def test_that_token_was_delivered_to_registering_user(self) -> None:
        expected_mail = "mailtest321@cp.org"
        request_args = DEFAULT.copy()
        request_args.pop("email")
        self.use_case.register_company(
            RegisterCompany.Request(email=expected_mail, **request_args)
        )
        expected_company = [
            company.id for company in self.company_repo.get_companies()
        ][0]
        self.assertEqual(
            self.token_delivery.presented_company_tokens[0].user,
            expected_company,
        )

    def test_that_registering_company_is_possible(self) -> None:
        request = RegisterCompany.Request(**DEFAULT)
        response = self.use_case.register_company(request)
        self.assertFalse(response.is_rejected)

    def test_that_correct_error_is_raised_when_user_with_mail_exists(self) -> None:
        self.company_generator.create_company_entity(email="test@cp.org")
        request = RegisterCompany.Request(**DEFAULT)
        response = self.use_case.register_company(request)
        self.assertTrue(response.is_rejected)
        self.assertEqual(
            response.rejection_reason,
            RegisterCompany.Response.RejectionReason.company_already_exists,
        )

    def test_that_registering_a_company_does_create_all_company_accounts(self) -> None:
        self.use_case.register_company(RegisterCompany.Request(**DEFAULT))
        assert len(self.account_repository.accounts) == 4
        for account in self.account_repository.accounts:
            assert account.account_type in (
                AccountTypes.a,
                AccountTypes.p,
                AccountTypes.r,
                AccountTypes.prd,
            )

    def test_that_correct_member_attributes_are_registered(self) -> None:
        request = RegisterCompany.Request(**DEFAULT)
        self.use_case.register_company(request)
        assert len(self.company_repo.get_companies()) == 1
        for company in self.company_repo.get_companies():
            assert company.email == request.email
            assert company.name == request.name
            assert company.registered_on is not None
            assert company.confirmed_on is None
