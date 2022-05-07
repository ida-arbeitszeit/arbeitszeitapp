from typing import Protocol


class AccountantInvitationPresenter(Protocol):
    def send_accountant_invitation(self, email: str, token: str) -> None:
        ...
