from functools import wraps
from typing import List, Optional

from flask_sqlalchemy import SQLAlchemy

from arbeitszeit import entities
from arbeitszeit import repositories as interfaces
from arbeitszeit.accountant_notifications import NotifyAccountantsAboutNewPlanPresenter
from arbeitszeit.control_thresholds import ControlThresholds
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.injector import (
    Binder,
    CallableProvider,
    ClassProvider,
    Injector,
    Module,
)
from arbeitszeit.token import (
    CompanyRegistrationMessagePresenter,
    InvitationTokenValidator,
    MemberRegistrationMessagePresenter,
    TokenService,
)
from arbeitszeit_flask.control_thresholds import ControlThresholdsFlask
from arbeitszeit_flask.database import get_social_accounting
from arbeitszeit_flask.database.repositories import (
    AccountantRepository,
    AccountOwnerRepository,
    AccountRepository,
    CompanyRepository,
    CooperationRepository,
    MemberRepository,
    PayoutFactorRepository,
    PlanDraftRepository,
    PlanRepository,
    PurchaseRepository,
    TransactionRepository,
    UserAddressBookImpl,
    WorkerInviteRepository,
)
from arbeitszeit_flask.datetime import RealtimeDatetimeService
from arbeitszeit_flask.extensions import db
from arbeitszeit_flask.flask_colors import FlaskColors
from arbeitszeit_flask.flask_plotter import FlaskPlotter
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.language_repository import LanguageRepositoryImpl
from arbeitszeit_flask.mail_service import (
    FlaskEmailConfiguration,
    MailService,
    get_mail_service,
)
from arbeitszeit_flask.notifications import FlaskFlashNotifier
from arbeitszeit_flask.template import (
    AccountantTemplateIndex,
    CompanyTemplateIndex,
    FlaskTemplateRenderer,
    MemberRegistrationEmailTemplateImpl,
    MemberTemplateIndex,
    TemplateIndex,
    TemplateRenderer,
)
from arbeitszeit_flask.text_renderer import TextRendererImpl
from arbeitszeit_flask.token import FlaskTokenService
from arbeitszeit_flask.translator import FlaskTranslator
from arbeitszeit_flask.url_index import CompanyUrlIndex, GeneralUrlIndex
from arbeitszeit_web.colors import Colors
from arbeitszeit_web.email import EmailConfiguration, UserAddressBook
from arbeitszeit_web.language_service import LanguageService
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.plotter import Plotter
from arbeitszeit_web.presenters.notify_accountant_about_new_plan_presenter import (
    NotifyAccountantsAboutNewPlanPresenterImpl,
)
from arbeitszeit_web.presenters.registration_email_presenter import (
    RegistrationEmailPresenter,
    RegistrationEmailTemplate,
)
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session
from arbeitszeit_web.text_renderer import TextRenderer
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import (
    HidePlanUrlIndex,
    LanguageChangerUrlIndex,
    RenewPlanUrlIndex,
    UrlIndex,
)


class AccountantModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[TemplateIndex] = ClassProvider(AccountantTemplateIndex)  # type: ignore


class MemberModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[TemplateIndex] = ClassProvider(MemberTemplateIndex)  # type: ignore


class CompanyModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[RenewPlanUrlIndex] = ClassProvider(CompanyUrlIndex)  # type: ignore
        binder[HidePlanUrlIndex] = ClassProvider(CompanyUrlIndex)  # type: ignore
        binder[TemplateIndex] = ClassProvider(CompanyTemplateIndex)  # type: ignore


class FlaskModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder.bind(
            interfaces.PurchaseRepository,  # type: ignore
            to=ClassProvider(PurchaseRepository),
        )
        binder.bind(
            entities.SocialAccounting,
            to=CallableProvider(get_social_accounting),
        )
        binder.bind(
            interfaces.AccountRepository,  # type: ignore
            to=ClassProvider(AccountRepository),
        )
        binder.bind(
            interfaces.MemberRepository,  # type: ignore
            to=ClassProvider(MemberRepository),
        )
        binder.bind(
            interfaces.CompanyRepository,  # type: ignore
            to=ClassProvider(CompanyRepository),
        )
        binder.bind(
            interfaces.PurchaseRepository,  # type: ignore
            to=ClassProvider(PurchaseRepository),
        )
        binder.bind(
            interfaces.PlanRepository,  # type: ignore
            to=ClassProvider(PlanRepository),
        )
        binder.bind(
            interfaces.AccountOwnerRepository,  # type: ignore
            to=ClassProvider(AccountOwnerRepository),
        )
        binder.bind(
            interfaces.PlanDraftRepository,  # type: ignore
            to=ClassProvider(PlanDraftRepository),
        )
        binder.bind(
            DatetimeService,  # type: ignore
            to=ClassProvider(RealtimeDatetimeService),
        )
        binder.bind(
            interfaces.WorkerInviteRepository,  # type: ignore
            to=ClassProvider(WorkerInviteRepository),
        )
        binder.bind(
            SQLAlchemy,
            to=CallableProvider(self.provide_sqlalchemy, is_singleton=True),
        )
        binder.bind(
            interfaces.CooperationRepository,  # type: ignore
            to=ClassProvider(CooperationRepository),
        )
        binder.bind(TokenService, to=ClassProvider(FlaskTokenService))  # type: ignore
        binder.bind(UserAddressBook, to=ClassProvider(UserAddressBookImpl))  # type: ignore
        binder.bind(
            interfaces.PayoutFactorRepository,  # type: ignore
            to=ClassProvider(PayoutFactorRepository),
        )
        binder[NotifyAccountantsAboutNewPlanPresenter] = ClassProvider(NotifyAccountantsAboutNewPlanPresenterImpl)  # type: ignore
        binder[TextRenderer] = ClassProvider(TextRendererImpl)  # type: ignore
        binder[Request] = ClassProvider(FlaskRequest)  # type: ignore
        binder[UrlIndex] = ClassProvider(GeneralUrlIndex)  # type: ignore
        binder[InvitationTokenValidator] = ClassProvider(FlaskTokenService)  # type: ignore
        binder[RegistrationEmailTemplate] = ClassProvider(MemberRegistrationEmailTemplateImpl)  # type: ignore
        binder[interfaces.LanguageRepository] = ClassProvider(LanguageRepositoryImpl)  # type: ignore
        binder[LanguageService] = ClassProvider(LanguageRepositoryImpl)  # type: ignore
        binder[EmailConfiguration] = ClassProvider(FlaskEmailConfiguration)  # type: ignore
        binder[interfaces.TransactionRepository] = ClassProvider(TransactionRepository)  # type: ignore
        binder[interfaces.AccountantRepository] = ClassProvider(AccountantRepository)  # type: ignore
        binder[TemplateRenderer] = ClassProvider(FlaskTemplateRenderer)  # type: ignore
        binder[Session] = ClassProvider(FlaskSession)  # type: ignore
        binder[Notifier] = ClassProvider(FlaskFlashNotifier)  # type: ignore
        binder[MailService] = CallableProvider(get_mail_service)  # type: ignore
        binder[Translator] = ClassProvider(FlaskTranslator)  # type: ignore
        binder[Plotter] = ClassProvider(FlaskPlotter)  # type: ignore
        binder[Colors] = ClassProvider(FlaskColors)  # type: ignore
        binder[ControlThresholds] = ClassProvider(ControlThresholdsFlask)  # type: ignore
        binder[LanguageChangerUrlIndex] = ClassProvider(GeneralUrlIndex)  # type: ignore
        binder[CompanyRegistrationMessagePresenter] = ClassProvider(  # type: ignore
            RegistrationEmailPresenter
        )
        binder[MemberRegistrationMessagePresenter] = ClassProvider(  # type: ignore
            RegistrationEmailPresenter
        )

    @staticmethod
    def provide_sqlalchemy() -> SQLAlchemy:
        return db


class with_injection:
    def __init__(self, modules: Optional[List[Module]] = None) -> None:
        self._modules = modules if modules is not None else []
        all_modules: List[Module] = []
        all_modules.append(FlaskModule())
        all_modules += self._modules
        self._injector = Injector(all_modules)

    def __call__(self, original_function):
        """When you wrap a function, make sure that the parameters to be
        injected come after the the parameters that the caller should
        provide.
        """

        @wraps(original_function)
        def wrapped_function(*args, **kwargs):
            return self._injector.call_with_injection(
                original_function, args=args, kwargs=kwargs
            )

        return wrapped_function

    @property
    def injector(self) -> Injector:
        return self._injector
