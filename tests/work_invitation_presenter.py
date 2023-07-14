from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.injector import singleton


@singleton
class InviteWorkerPresenterImpl:
    @dataclass
    class Invite:
        id: UUID
        worker_email: str

    def __init__(self) -> None:
        self.invites: list[InviteWorkerPresenterImpl.Invite] = []

    def show_invite_worker_message(self, worker_email: str, invite: UUID) -> None:
        self.invites.append(
            InviteWorkerPresenterImpl.Invite(id=invite, worker_email=worker_email)
        )
