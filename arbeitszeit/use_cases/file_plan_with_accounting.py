from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.repositories import PlanDraftRepository


@dataclass
class FilePlanWithAccounting:
    @dataclass
    class Request:
        draft_id: UUID

    @dataclass
    class Response:
        is_plan_successfully_filed: bool

    draft_repository: PlanDraftRepository

    def file_plan_with_accounting(self, request: Request) -> Response:
        draft = self.draft_repository.get_by_id(id=request.draft_id)
        self.draft_repository.delete_draft(id=request.draft_id)
        return self.Response(
            is_plan_successfully_filed=draft is not None,
        )
