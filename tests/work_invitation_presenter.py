from dataclasses import dataclass

from arbeitszeit.injector import singleton


@singleton
class InviteWorkerPresenterImpl:
    @dataclass
    class Invite:
        worker_email: str

    def __init__(self) -> None:
        self.invites: list[InviteWorkerPresenterImpl.Invite] = []

    def show_invite_worker_message(self, worker_email: str) -> None:
        self.invites.append(InviteWorkerPresenterImpl.Invite(worker_email=worker_email))
