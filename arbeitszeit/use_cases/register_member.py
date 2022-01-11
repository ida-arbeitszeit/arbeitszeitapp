from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import AccountTypes
from arbeitszeit.errors import CannotSendEmail
from arbeitszeit.mail_service import MailService
from arbeitszeit.repositories import AccountRepository, MemberRepository
from arbeitszeit.token import TokenService


@dataclass
class RegisterMemberResponse:
    class RejectionReason(Exception, Enum):
        member_already_exists = auto()
        sending_mail_failed = auto()

    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass
class RegisterMemberRequest:
    email: str
    name: str
    password: str
    email_sender: str
    template_name: str
    endpoint: str


@inject
@dataclass
class RegisterMember:
    account_repository: AccountRepository
    member_repository: MemberRepository
    datetime_service: DatetimeService
    mail_service: MailService
    token_service: TokenService

    def __call__(self, request: RegisterMemberRequest) -> RegisterMemberResponse:
        try:
            self._register_member(request)
            html = self._create_confirmation_mail(request)
            self._send_confirmation_mail(request, html)
        except RegisterMemberResponse.RejectionReason as reason:
            return RegisterMemberResponse(rejection_reason=reason)
        return RegisterMemberResponse(rejection_reason=None)

    def _register_member(self, request: RegisterMemberRequest) -> None:
        if self.member_repository.has_member_with_email(request.email):
            raise RegisterMemberResponse.RejectionReason.member_already_exists

        member_account = self.account_repository.create_account(AccountTypes.member)
        registered_on = self.datetime_service.now()
        self.member_repository.create_member(
            request.email, request.name, request.password, member_account, registered_on
        )

    def _create_confirmation_mail(self, request: RegisterMemberRequest) -> str:
        token = self.token_service.generate_token(request.email)
        html = self.mail_service.create_confirmation_html(
            request.template_name, request.endpoint, token
        )
        return html

    def _send_confirmation_mail(
        self, request: RegisterMemberRequest, html: str
    ) -> None:
        try:
            self.mail_service.send_message(
                subject="Bitte bestätige dein Konto",
                recipients=[request.email],
                html=html,
                sender=request.email_sender,
            )
        except CannotSendEmail:
            raise RegisterMemberResponse.RejectionReason.sending_mail_failed
