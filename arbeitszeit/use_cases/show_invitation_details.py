from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import WorkerInviteRepository


@dataclass
class ShowInvitationDetailsRequest:
    invite_id: UUID
    user: UUID


@dataclass
class ShowInvitationDetailsResponse:
    is_success: bool


@inject
@dataclass
class ShowInvitationDetailsUseCase:
    invite_repository: WorkerInviteRepository

    def show_invitation_details(
        self, request: ShowInvitationDetailsRequest
    ) -> ShowInvitationDetailsResponse:
        invite = self.invite_repository.get_by_id(request.invite_id)
        if invite is not None and request.user == invite.member.id:
            return ShowInvitationDetailsResponse(is_success=True)
        else:
            return ShowInvitationDetailsResponse(is_success=False)
