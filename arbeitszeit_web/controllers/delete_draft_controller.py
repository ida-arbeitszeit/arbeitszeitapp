from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.use_cases.delete_draft import DeleteDraftUseCase
from arbeitszeit_web.session import Session


@inject
@dataclass
class DeleteDraftController:
    class Failure(Exception):
        pass

    session: Session

    def get_request(self, draft: UUID) -> DeleteDraftUseCase.Request:
        current_user = self.session.get_current_user()
        if current_user is None:
            raise self.Failure()
        return DeleteDraftUseCase.Request(
            deleter=current_user,
            draft=draft,
        )
