from functools import wraps
from typing import List, Optional

from flask_sqlalchemy import SQLAlchemy

from arbeitszeit import records
from arbeitszeit import repositories as interfaces
from arbeitszeit.control_thresholds import ControlThresholds
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.email_notifications import EmailSender
from arbeitszeit.injector import (
    AliasProvider,
    Binder,
    CallableProvider,
    Injector,
    Module,
)
from arbeitszeit.password_hasher import PasswordHasher
from arbeitszeit_flask.control_thresholds import ControlThresholdsFlask
from arbeitszeit_flask.database import get_social_accounting
from arbeitszeit_flask.database.repositories import (
    DatabaseGatewayImpl,
    UserAddressBookImpl,
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
from arbeitszeit_flask.password_hasher import PasswordHasherImpl
from arbeitszeit_flask.template import (
    AccountantTemplateIndex,
    CompanyTemplateIndex,
    FlaskTemplateRenderer,
    MemberTemplateIndex,
    TemplateIndex,
    TemplateRenderer,
)
from arbeitszeit_flask.text_renderer import TextRendererImpl
from arbeitszeit_flask.token import FlaskTokenService
from arbeitszeit_flask.translator import FlaskTranslator
from arbeitszeit_flask.url_index import CompanyUrlIndex, GeneralUrlIndex
from arbeitszeit_flask.views.accountant_invitation_email_view import (
    AccountantInvitationEmailViewImpl,
)
from arbeitszeit_web.colors import Colors
from arbeitszeit_web.email import EmailConfiguration, UserAddressBook
from arbeitszeit_web.email.accountant_invitation_presenter import (
    AccountantInvitationEmailView,
)
from arbeitszeit_web.email.email_sender import EmailSender as EmailSenderImpl
from arbeitszeit_web.language_service import LanguageService
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.plotter import Plotter
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session
from arbeitszeit_web.text_renderer import TextRenderer
from arbeitszeit_web.token import TokenService
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import (
    AccountantInvitationUrlIndex,
    HidePlanUrlIndex,
    LanguageChangerUrlIndex,
    RenewPlanUrlIndex,
    UrlIndex,
)


class AccountantModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[TemplateIndex] = AliasProvider(AccountantTemplateIndex)


class MemberModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[TemplateIndex] = AliasProvider(MemberTemplateIndex)


class CompanyModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[RenewPlanUrlIndex] = AliasProvider(CompanyUrlIndex)
        binder[HidePlanUrlIndex] = AliasProvider(CompanyUrlIndex)
        binder[TemplateIndex] = AliasProvider(CompanyTemplateIndex)


class FlaskModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder.bind(
            records.SocialAccounting,
            to=CallableProvider(get_social_accounting),
        )
        binder.bind(
            DatetimeService,
            to=AliasProvider(RealtimeDatetimeService),
        )
        binder.bind(
            SQLAlchemy,
            to=CallableProvider(self.provide_sqlalchemy, is_singleton=True),
        )
        binder.bind(UserAddressBook, to=AliasProvider(UserAddressBookImpl))
        binder[TextRenderer] = AliasProvider(TextRendererImpl)
        binder[Request] = AliasProvider(FlaskRequest)
        binder[UrlIndex] = AliasProvider(GeneralUrlIndex)
        binder[interfaces.LanguageRepository] = AliasProvider(LanguageRepositoryImpl)
        binder[LanguageService] = AliasProvider(LanguageRepositoryImpl)
        binder[EmailConfiguration] = AliasProvider(FlaskEmailConfiguration)
        binder.bind(
            interfaces.DatabaseGateway,
            to=AliasProvider(DatabaseGatewayImpl),
        )
        binder[TemplateRenderer] = AliasProvider(FlaskTemplateRenderer)
        binder[Session] = AliasProvider(FlaskSession)
        binder[Notifier] = AliasProvider(FlaskFlashNotifier)
        binder[MailService] = CallableProvider(get_mail_service)
        binder[Translator] = AliasProvider(FlaskTranslator)
        binder[Plotter] = AliasProvider(FlaskPlotter)
        binder[Colors] = AliasProvider(FlaskColors)
        binder[ControlThresholds] = AliasProvider(ControlThresholdsFlask)
        binder[LanguageChangerUrlIndex] = AliasProvider(GeneralUrlIndex)
        binder.bind(
            AccountantInvitationEmailView,
            to=AliasProvider(AccountantInvitationEmailViewImpl),
        )
        binder.bind(
            AccountantInvitationUrlIndex,
            to=AliasProvider(GeneralUrlIndex),
        )
        binder.bind(
            PasswordHasher,
            to=AliasProvider(PasswordHasherImpl),
        )
        binder.bind(
            TokenService,
            to=AliasProvider(FlaskTokenService),
        )
        binder.bind(
            EmailSender,
            to=AliasProvider(EmailSenderImpl),
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
