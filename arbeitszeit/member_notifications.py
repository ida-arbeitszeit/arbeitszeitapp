from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.presenters import InviteWorkerPresenter as Presenter
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class MemberNotifier:
    presenter: Presenter
    database: DatabaseGateway

    def notify_member_about_invitation(self, member: UUID, invite: UUID) -> None:
        record = (
            self.database.get_members()
            .with_id(member)
            .joined_with_email_address()
            .first()
        )
        if record is not None:
            _, member_email = record
            self.presenter.show_invite_worker_message(
                worker_email=member_email.address, invite=invite
            )
