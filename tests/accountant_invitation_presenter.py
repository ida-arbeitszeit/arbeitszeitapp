from dataclasses import dataclass
from typing import List

from arbeitszeit.injector import singleton
from arbeitszeit_web.token import TokenService


@singleton
class AccountantInvitationPresenterTestImpl:
    @dataclass
    class Invitation:
        email: str
        token: str

    def __init__(self, token_service: TokenService) -> None:
        self.invitations: List[AccountantInvitationPresenterTestImpl.Invitation] = []
        self.token_service = token_service

    def send_accountant_invitation(self, email: str) -> None:
        token = self.token_service.generate_token(email)
        self.invitations.append(self.Invitation(email=email, token=token))
