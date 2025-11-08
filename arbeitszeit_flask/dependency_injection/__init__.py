from __future__ import annotations

from functools import wraps
from typing import List, Optional

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
from arbeitszeit_db import get_social_accounting
from arbeitszeit_db.db import Database
from arbeitszeit_db.repositories import DatabaseGatewayImpl
from arbeitszeit_flask.control_thresholds import ControlThresholdsFlask
from arbeitszeit_flask.datetime import (
    FlaskDatetimeFormatter,
    FlaskTimezoneConfiguration,
    RealtimeDatetimeService,
)
from arbeitszeit_flask.email_configuration import FlaskEmailConfiguration
from arbeitszeit_flask.flask_colors import FlaskColors
from arbeitszeit_flask.flask_plotter import FlaskPlotter
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.language_repository import LanguageRepositoryImpl
from arbeitszeit_flask.mail_service import get_mail_service
from arbeitszeit_flask.notifications import FlaskFlashNotifier
from arbeitszeit_flask.password_hasher import provide_password_hasher
from arbeitszeit_flask.text_renderer import TextRendererImpl
from arbeitszeit_flask.token import FlaskTokenService
from arbeitszeit_flask.translator import FlaskTranslator
from arbeitszeit_flask.url_index import GeneralUrlIndex
from arbeitszeit_flask.views.accountant_invitation_email_view import (
    AccountantInvitationEmailViewImpl,
)
from arbeitszeit_web.colors import HexColors
from arbeitszeit_web.email import EmailConfiguration, MailService
from arbeitszeit_web.email.accountant_invitation_presenter import (
    AccountantInvitationEmailView,
)
from arbeitszeit_web.email.email_sender import EmailSender as EmailSenderImpl
from arbeitszeit_web.formatters.datetime_formatter import (
    DatetimeFormatter,
    TimezoneConfiguration,
)
from arbeitszeit_web.language_service import LanguageService
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.plotter import Plotter
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session
from arbeitszeit_web.text_renderer import TextRenderer
from arbeitszeit_web.token import TokenService
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


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
            Database,
            to=CallableProvider(self.provide_database, is_singleton=True),
        )
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
        binder[Session] = AliasProvider(FlaskSession)
        binder[Notifier] = AliasProvider(FlaskFlashNotifier)
        binder[MailService] = CallableProvider(get_mail_service)
        binder[Translator] = AliasProvider(FlaskTranslator)
        binder[Plotter] = AliasProvider(FlaskPlotter)
        binder[HexColors] = AliasProvider(FlaskColors)
        binder[ControlThresholds] = AliasProvider(ControlThresholdsFlask)
        binder[DatetimeFormatter] = AliasProvider(FlaskDatetimeFormatter)
        binder[TimezoneConfiguration] = AliasProvider(FlaskTimezoneConfiguration)
        binder.bind(
            AccountantInvitationEmailView,
            to=AliasProvider(AccountantInvitationEmailViewImpl),
        )
        binder.bind(
            PasswordHasher,
            to=CallableProvider(provide_password_hasher),
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
    def provide_database() -> Database:
        #  db gets confiured in create_app
        return Database()


class with_injection:
    def __init__(self, modules: Optional[List[Module]] = None) -> None:
        self._injector = create_dependency_injector(modules)

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


def create_dependency_injector(
    additional_modules: Optional[List[Module]] = None,
) -> Injector:
    return Injector(
        [FlaskModule()] + (additional_modules if additional_modules else [])
    )
