from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway, PlanDraftRepository


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

    database: DatabaseGateway
    draft_repository: PlanDraftRepository

    def delete_draft(self, request: Request) -> Response:
        deleter = self.database.get_companies().with_id(request.deleter).first()
        draft_query = self.draft_repository.get_plan_drafts().with_id(request.draft)
        draft = draft_query.first()
        if not draft or not deleter:
            raise self.Failure()
        if draft.planner != deleter.id:
            raise self.Failure()
        draft_query.delete()
        return self.Response(product_name=draft.product_name)
