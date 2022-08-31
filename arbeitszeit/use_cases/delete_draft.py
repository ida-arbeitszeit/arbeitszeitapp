from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import CompanyRepository, PlanDraftRepository


@inject
@dataclass
class DeleteDraftUseCase:
    @dataclass
    class Request:
        deleter: UUID
        draft: UUID

    @dataclass
    class Response:
        pass

    class Failure(Exception):
        pass

    company_repository: CompanyRepository
    draft_repository: PlanDraftRepository

    def delete_draft(self, request: Request) -> Response:
        deleter = self.company_repository.get_by_id(request.deleter)
        draft = self.draft_repository.get_by_id(request.draft)
        if not draft or not deleter:
            raise self.Failure()
        if draft.planner.id != deleter.id:
            raise self.Failure()
        self.draft_repository.delete_draft(request.draft)
        return self.Response()
