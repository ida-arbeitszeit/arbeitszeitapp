from arbeitszeit.entities import AccountTypes
from arbeitszeit.use_cases import (
    RegisterCompany,
    RegisterCompanyRequest,
    RegisterCompanyResponse,
)
from tests.data_generators import CompanyGenerator
from tests.mail_service import FakeMailService

from .dependency_injection import injection_test
from .repositories import AccountRepository, CompanyRepository

DEFAULT = dict(
    email="test@cp.org",
    name="test name",
    password="super safe",
    email_sender="we@cp.org",
    template_name="email_template.html",
    endpoint="auth.test",
)


@injection_test
def test_that_registering_company_is_possible(
    use_case: RegisterCompany,
):
    request = RegisterCompanyRequest(**DEFAULT)
    response = use_case(request)
    assert not response.is_rejected


@injection_test
def test_that_registering_a_company_does_create_all_company_accounts(
    register_company: RegisterCompany, account_repository: AccountRepository
) -> None:
    register_company(RegisterCompanyRequest(**DEFAULT))
    assert len(account_repository.accounts) == 4
    for account in account_repository.accounts:
        assert account.account_type in (
            AccountTypes.a,
            AccountTypes.p,
            AccountTypes.r,
            AccountTypes.prd,
        )


@injection_test
def test_that_correct_member_attributes_are_registered(
    use_case: RegisterCompany,
    company_repo: CompanyRepository,
):
    request = RegisterCompanyRequest(**DEFAULT)
    use_case(request)
    assert len(company_repo.companies) == 1
    for company in company_repo.companies.values():
        assert company.email == request.email
        assert company.name == request.name
        assert company.registered_on is not None
        assert company.confirmed_on is None


@injection_test
def test_that_mail_is_sent(
    use_case: RegisterCompany,
    mail_service: FakeMailService,
):
    request = RegisterCompanyRequest(**DEFAULT)
    use_case(request)
    assert len(mail_service.sent_mails) == 1
    assert "Bitte bestätige dein Konto" in mail_service.sent_mails[0]
    assert DEFAULT["endpoint"] in mail_service.sent_mails[0]


@injection_test
def test_that_correct_error_is_raised_when_company_with_mail_exists(
    use_case: RegisterCompany, company_generator: CompanyGenerator
):
    company_generator.create_company(email="test@cp.org")
    request = RegisterCompanyRequest(**DEFAULT)
    response = use_case(request)
    assert response.is_rejected
    assert (
        response.rejection_reason
        == RegisterCompanyResponse.RejectionReason.company_already_exists
    )
