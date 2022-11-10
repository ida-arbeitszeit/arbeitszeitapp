from injector import Injector, Module, inject, provider, singleton

from arbeitszeit_web.create_cooperation import CreateCooperationPresenter
from arbeitszeit_web.email import EmailConfiguration, MailService, UserAddressBook
from arbeitszeit_web.get_company_transactions import GetCompanyTransactionsPresenter
from arbeitszeit_web.hide_plan import HidePlanPresenter
from arbeitszeit_web.invite_worker_to_company import InviteWorkerToCompanyPresenter
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.pay_consumer_product import PayConsumerProductPresenter
from arbeitszeit_web.presenters.accountant_invitation_presenter import (
    AccountantInvitationEmailPresenter,
)
from arbeitszeit_web.presenters.list_available_languages_presenter import (
    ListAvailableLanguagesPresenter,
)
from arbeitszeit_web.presenters.member_purchases import MemberPurchasesPresenter
from arbeitszeit_web.presenters.register_company_presenter import (
    RegisterCompanyPresenter,
)
from arbeitszeit_web.presenters.register_member_presenter import RegisterMemberPresenter
from arbeitszeit_web.presenters.send_work_certificates_to_worker_presenter import (
    SendWorkCertificatesToWorkerPresenter,
)
from arbeitszeit_web.request import Request
from arbeitszeit_web.request_cooperation import RequestCooperationPresenter
from arbeitszeit_web.session import Session
from arbeitszeit_web.url_index import HidePlanUrlIndex, RenewPlanUrlIndex, UrlIndex
from tests.datetime_service import FakeDatetimeService
from tests.dependency_injection import TestingModule
from tests.email import FakeAddressBook, FakeEmailConfiguration, FakeEmailSender
from tests.language_service import FakeLanguageService
from tests.request import FakeRequest
from tests.session import FakeSession
from tests.translator import FakeTranslator
from tests.use_cases.dependency_injection import InMemoryModule

from .accountant_invitation_email_view import AccountantInvitationEmailViewImpl
from .notifier import NotifierTestImpl
from .url_index import (
    AccountantInvitationUrlIndexImpl,
    HidePlanUrlIndexTestImpl,
    LanguageChangerUrlIndexImpl,
    RenewPlanUrlIndexTestImpl,
    UrlIndexTestImpl,
)


class PresenterTestsInjector(Module):
    @provider
    def provide_email_configuration(
        self, instance: FakeEmailConfiguration
    ) -> EmailConfiguration:
        return instance

    @provider
    def provide_mail_service(self, instance: FakeEmailSender) -> MailService:
        return instance

    @provider
    def provide_user_address_book(self, instance: FakeAddressBook) -> UserAddressBook:
        return instance

    @provider
    def provide_request(self, request: FakeRequest) -> Request:
        return request

    @provider
    def provide_hide_plan_url_index(
        self, index: HidePlanUrlIndexTestImpl
    ) -> HidePlanUrlIndex:
        return index

    @provider
    def provide_renew_plan_url_index(
        self, index: RenewPlanUrlIndexTestImpl
    ) -> RenewPlanUrlIndex:
        return index

    @provider
    def provide_session(self, session: FakeSession) -> Session:
        return session

    @singleton
    @provider
    def provide_fake_request(self) -> FakeRequest:
        return FakeRequest()

    @singleton
    @provider
    def provide_notifier_test_impl(self) -> NotifierTestImpl:
        return NotifierTestImpl()

    @provider
    def provide_notifier(self, notifier: NotifierTestImpl) -> Notifier:
        return notifier

    @singleton
    @provider
    def provide_plan_summary_url_index_test_impl(self) -> UrlIndexTestImpl:
        return UrlIndexTestImpl()

    @provider
    def provide_url_index(self, index: UrlIndexTestImpl) -> UrlIndex:
        return index  # type: ignore

    @provider
    def provide_create_cooperation_presenter(
        self, notifier: Notifier, translator: FakeTranslator
    ) -> CreateCooperationPresenter:
        return CreateCooperationPresenter(
            user_notifier=notifier,
            translator=translator,
        )

    @provider
    def provide_request_cooperation_presenter(
        self,
        translator: FakeTranslator,
        mail_service: FakeEmailSender,
        email_configuration: FakeEmailConfiguration,
    ) -> RequestCooperationPresenter:
        return RequestCooperationPresenter(
            translator=translator,
            mail_service=mail_service,
            email_configuration=email_configuration,
        )

    @provider
    def provide_hide_plan_presenter(
        self, notifier: Notifier, translator: FakeTranslator
    ) -> HidePlanPresenter:
        return HidePlanPresenter(
            notifier=notifier,
            trans=translator,
        )

    @provider
    def provide_pay_consumer_product_presenter(
        self, notifier: Notifier, translator: FakeTranslator
    ) -> PayConsumerProductPresenter:
        return PayConsumerProductPresenter(
            user_notifier=notifier,
            translator=translator,
        )

    @provider
    def provide_send_work_certificates_to_worker_presenter(
        self, notifier: Notifier, translator: FakeTranslator
    ) -> SendWorkCertificatesToWorkerPresenter:
        return SendWorkCertificatesToWorkerPresenter(
            notifier=notifier,
            translator=translator,
        )

    @provider
    def provide_register_member_presenter(
        self, session: FakeSession, translator: FakeTranslator
    ) -> RegisterMemberPresenter:
        return RegisterMemberPresenter(session=session, translator=translator)

    @provider
    def provide_register_company_presenter(
        self, session: FakeSession, translator: FakeTranslator
    ) -> RegisterCompanyPresenter:
        return RegisterCompanyPresenter(translator=translator, session=session)

    @singleton
    @provider
    def provide_accountant_invitation_email_view(
        self,
    ) -> AccountantInvitationEmailViewImpl:
        return AccountantInvitationEmailViewImpl()

    @provider
    def provide_accountant_invitation_presenter_impl(
        self,
        invitation_view: AccountantInvitationEmailViewImpl,
        translator: FakeTranslator,
        email_configuration: FakeEmailConfiguration,
        invitation_url_index: AccountantInvitationUrlIndexImpl,
    ) -> AccountantInvitationEmailPresenter:
        return AccountantInvitationEmailPresenter(
            invitation_view=invitation_view,
            translator=translator,
            email_configuration=email_configuration,
            invitation_url_index=invitation_url_index,
        )

    @provider
    def provide_get_company_transactions_presenter(
        self, translator: FakeTranslator, datetime_service: FakeDatetimeService
    ) -> GetCompanyTransactionsPresenter:
        return GetCompanyTransactionsPresenter(
            translator=translator, datetime_service=datetime_service
        )

    @provider
    def provide_invite_worker_to_company_presenter(
        self, translator: FakeTranslator
    ) -> InviteWorkerToCompanyPresenter:
        return InviteWorkerToCompanyPresenter(translator=translator)

    @provider
    def provide_list_available_languages_presenter(
        self,
        language_changer_url_index: LanguageChangerUrlIndexImpl,
        language_service: FakeLanguageService,
    ) -> ListAvailableLanguagesPresenter:
        return ListAvailableLanguagesPresenter(
            language_changer_url_index=language_changer_url_index,
            language_service=language_service,
        )

    @provider
    def provide_member_purchase_provider(
        self, datetime_service: FakeDatetimeService
    ) -> MemberPurchasesPresenter:
        return MemberPurchasesPresenter(
            datetime_service=datetime_service,
        )


def get_dependency_injector() -> Injector:
    return Injector(
        modules=[TestingModule(), InMemoryModule(), PresenterTestsInjector()]
    )


def injection_test(original_test):
    injector = get_dependency_injector()

    def wrapper(*args, **kwargs):
        return injector.call_with_injection(
            inject(original_test), args=args, kwargs=kwargs
        )

    return wrapper
