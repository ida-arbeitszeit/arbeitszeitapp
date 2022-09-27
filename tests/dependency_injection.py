from injector import provider, singleton

from arbeitszeit.control_thresholds import ControlThresholds
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.dependency_injection import ArbeitszeitModule
from arbeitszeit.repositories import (
    CompanyRepository,
    CompanyWorkerRepository,
    MemberRepository,
)
from arbeitszeit.use_cases.send_accountant_registration_token.accountant_invitation_presenter import (
    AccountantInvitationPresenter,
)
from arbeitszeit_web.colors import Colors
from arbeitszeit_web.plotter import Plotter
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator
from tests.accountant_invitation_presenter import AccountantInvitationPresenterTestImpl
from tests.company import CompanyManager
from tests.control_thresholds import ControlThresholdsTestImpl
from tests.datetime_service import FakeDatetimeService
from tests.email import FakeEmailSender
from tests.language_service import FakeLanguageService
from tests.plotter import FakePlotter
from tests.presenters.test_colors import ColorsTestImpl
from tests.request import FakeRequest
from tests.session import FakeSession
from tests.token import FakeTokenService
from tests.translator import FakeTranslator


class TestingModule(ArbeitszeitModule):
    @provider
    def provide_colors(self, colors: ColorsTestImpl) -> Colors:
        return colors

    @provider
    def provide_plotter(self, plotter: FakePlotter) -> Plotter:
        return plotter

    @provider
    def provide_control_thresholds(
        self, thresholds: ControlThresholdsTestImpl
    ) -> ControlThresholds:
        return thresholds

    @provider
    def provide_translator(self, translator: FakeTranslator) -> Translator:
        return translator

    @singleton
    @provider
    def provide_language_service(self) -> FakeLanguageService:
        return FakeLanguageService()

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

    @singleton
    @provider
    def provide_session(self, instance: FakeSession) -> Session:
        return instance

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

    @singleton
    @provider
    def provide_fake_datetime_service(self) -> FakeDatetimeService:
        return FakeDatetimeService()

    @provider
    def provide_datetime_service(self, service: FakeDatetimeService) -> DatetimeService:
        return service

    @singleton
    @provider
    def provide_fake_request(self) -> FakeRequest:
        return FakeRequest()
