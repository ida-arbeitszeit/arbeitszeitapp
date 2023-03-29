from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.repositories import CompanyRepository, PlanDraftRepository


@dataclass
class DeleteDraftUseCase:
    @dataclass
    class Request:
        deleter: UUID
        draft: UUID

    @dataclass
    class Response:
        product_name: str

    class Failure(Exception):
        pass

    company_repository: CompanyRepository
    draft_repository: PlanDraftRepository

    def delete_draft(self, request: Request) -> Response:
        deleter = (
            self.company_repository.get_companies().with_id(request.deleter).first()
        )
        draft = self.draft_repository.get_by_id(request.draft)
        if not draft or not deleter:
            raise self.Failure()
        if draft.planner != deleter.id:
            raise self.Failure()
        self.draft_repository.delete_draft(request.draft)
        return self.Response(product_name=draft.product_name)
