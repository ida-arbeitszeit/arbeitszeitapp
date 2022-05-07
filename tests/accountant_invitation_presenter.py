from dataclasses import dataclass
from typing import List


class AccountantInvitationPresenterTestImpl:
    @dataclass
    class Invitation:
        email: str
        token: str

    def __init__(self) -> None:
        self.invitations: List[AccountantInvitationPresenterTestImpl.Invitation] = []

    def send_accountant_invitation(self, email: str, token: str) -> None:
        self.invitations.append(self.Invitation(email=email, token=token))
