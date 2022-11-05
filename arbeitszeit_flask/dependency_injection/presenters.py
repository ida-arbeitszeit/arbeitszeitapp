from injector import Module, provider

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.use_cases.register_company.company_registration_message_presenter import (
    CompanyRegistrationMessagePresenter,
)
from arbeitszeit.use_cases.register_member.member_registration_message_presenter import (
    MemberRegistrationMessagePresenter,
)
from arbeitszeit.use_cases.send_accountant_registration_token.accountant_invitation_presenter import (
    AccountantInvitationPresenter,
)
from arbeitszeit_flask.url_index import GeneralUrlIndex
from arbeitszeit_web.email import EmailConfiguration, MailService, UserAddressBook
from arbeitszeit_web.get_company_transactions import GetCompanyTransactionsPresenter
from arbeitszeit_web.invite_worker_to_company import InviteWorkerToCompanyPresenter
from arbeitszeit_web.language_service import LanguageService
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.presenters.accountant_invitation_presenter import (
    AccountantInvitationEmailPresenter,
    AccountantInvitationEmailView,
)
from arbeitszeit_web.presenters.list_available_languages_presenter import (
    ListAvailableLanguagesPresenter,
)
from arbeitszeit_web.presenters.member_purchases import MemberPurchasesPresenter
from arbeitszeit_web.presenters.register_accountant_presenter import (
    RegisterAccountantPresenter,
)
from arbeitszeit_web.presenters.register_company_presenter import (
    RegisterCompanyPresenter,
)
from arbeitszeit_web.presenters.register_member_presenter import RegisterMemberPresenter
from arbeitszeit_web.presenters.registration_email_presenter import (
    RegistrationEmailPresenter,
    RegistrationEmailTemplate,
)
from arbeitszeit_web.presenters.send_confirmation_email_presenter import (
    SendConfirmationEmailPresenter,
)
from arbeitszeit_web.presenters.send_work_certificates_to_worker_presenter import (
    SendWorkCertificatesToWorkerPresenter,
)
from arbeitszeit_web.request_cooperation import RequestCooperationPresenter
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import ConfirmationUrlIndex


class CompanyPresenterModule(Module):
    @provider
    def provide_request_cooperation_presenter(
        self,
        translator: Translator,
        mail_service: MailService,
        email_configuration: EmailConfiguration,
    ) -> RequestCooperationPresenter:
        return RequestCooperationPresenter(
            translator, mail_service, email_configuration
        )

    @provider
    def provide_send_work_certificates_to_worker_presenter(
        self, notifier: Notifier, translator: Translator
    ) -> SendWorkCertificatesToWorkerPresenter:
        return SendWorkCertificatesToWorkerPresenter(notifier, translator)

    @provider
    def provide_get_company_transactions_presenter(
        self, translator: Translator, datetime_service: DatetimeService
    ) -> GetCompanyTransactionsPresenter:
        return GetCompanyTransactionsPresenter(
            translator=translator, datetime_service=datetime_service
        )


class PresenterModule(Module):
    @provider
    def provide_register_accountant_presenter(
        self,
        notifier: Notifier,
        session: Session,
        translator: Translator,
        dashboard_url_index: GeneralUrlIndex,
    ) -> RegisterAccountantPresenter:
        return RegisterAccountantPresenter(
            notifier=notifier,
            session=session,
            translator=translator,
            dashboard_url_index=dashboard_url_index,
        )

    @provider
    def provide_accountant_invitation_presenter(
        self,
        view: AccountantInvitationEmailView,
        email_configuration: EmailConfiguration,
        translator: Translator,
        invitation_url_index: GeneralUrlIndex,
    ) -> AccountantInvitationPresenter:
        return AccountantInvitationEmailPresenter(
            invitation_view=view,
            email_configuration=email_configuration,
            translator=translator,
            invitation_url_index=invitation_url_index,
        )

    @provider
    def provide_register_member_presenter(
        self, session: Session, translator: Translator
    ) -> RegisterMemberPresenter:
        return RegisterMemberPresenter(session=session, translator=translator)

    @provider
    def provide_register_company_presenter(
        self, session: Session, translator: Translator
    ) -> RegisterCompanyPresenter:
        return RegisterCompanyPresenter(session=session, translator=translator)

    @provider
    def provide_registration_email_presenter(
        self,
        email_sender: MailService,
        address_book: UserAddressBook,
        email_template: RegistrationEmailTemplate,
        url_index: ConfirmationUrlIndex,
        email_configuration: EmailConfiguration,
        translator: Translator,
    ) -> RegistrationEmailPresenter:
        return RegistrationEmailPresenter(
            email_sender=email_sender,
            address_book=address_book,
            member_email_template=email_template,
            company_email_template=email_template,
            url_index=url_index,
            email_configuration=email_configuration,
            translator=translator,
        )

    @provider
    def provide_member_registration_message_presenter(
        self, presenter: RegistrationEmailPresenter
    ) -> MemberRegistrationMessagePresenter:
        return presenter

    @provider
    def provide_company_registration_message_presenter(
        self, presenter: RegistrationEmailPresenter
    ) -> CompanyRegistrationMessagePresenter:
        return presenter

    @provider
    def provide_list_available_languages_presenter(
        self,
        language_changer_url_index: GeneralUrlIndex,
        language_service: LanguageService,
    ) -> ListAvailableLanguagesPresenter:
        return ListAvailableLanguagesPresenter(
            language_changer_url_index=language_changer_url_index,
            language_service=language_service,
        )

    @provider
    def provide_send_confirmation_email_presenter(
        self,
        url_index: ConfirmationUrlIndex,
        email_configuration: EmailConfiguration,
        translator: Translator,
    ) -> SendConfirmationEmailPresenter:
        return SendConfirmationEmailPresenter(
            url_index=url_index,
            email_configuration=email_configuration,
            translator=translator,
        )

    @provider
    def provide_invite_worker_to_company_presenter(
        self, translator: Translator
    ) -> InviteWorkerToCompanyPresenter:
        return InviteWorkerToCompanyPresenter(translator)

    @provider
    def provide_member_purchases_presenter(
        self,
        datetime_service: DatetimeService,
    ) -> MemberPurchasesPresenter:
        return MemberPurchasesPresenter(datetime_service=datetime_service)
