from injector import Module, provider, singleton

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import (
    CompanyRepository,
    CompanyWorkerRepository,
    MemberRepository,
)
from arbeitszeit.use_cases.send_accountant_registration_token.accountant_invitation_presenter import (
    AccountantInvitationPresenter,
)
from tests.accountant_invitation_presenter import AccountantInvitationPresenterTestImpl
from tests.company import CompanyManager
from tests.email import FakeEmailSender
from tests.session import FakeSession
from tests.token import FakeTokenService


class TestingModule(Module):
    @singleton
    @provider
    def provide_fake_email_service(self) -> FakeEmailSender:
        return FakeEmailSender()

    @provider
    def provide_company_manager(
        self,
        company_repository: CompanyRepository,
        member_repository: MemberRepository,
        company_worker_repository: CompanyWorkerRepository,
    ) -> CompanyManager:
        return CompanyManager(
            worker_repository=company_worker_repository,
            company_repository=company_repository,
            member_repository=member_repository,
        )

    @singleton
    @provider
    def provide_fake_session(self) -> FakeSession:
        return FakeSession()

    @provider
    def provide_fake_token_service(
        self, datetime_service: DatetimeService
    ) -> FakeTokenService:
        return FakeTokenService(datetime_service=datetime_service)

    @provider
    def provide_accountant_invitation_presenter(
        self, presenter: AccountantInvitationPresenterTestImpl
    ) -> AccountantInvitationPresenter:
        return presenter

    @singleton
    @provider
    def provide_accountant_invitation_presenter_test_impl(
        self,
    ) -> AccountantInvitationPresenterTestImpl:
        return AccountantInvitationPresenterTestImpl()
