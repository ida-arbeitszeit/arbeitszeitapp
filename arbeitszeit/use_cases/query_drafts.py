from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit.entities import PlanDraft
from arbeitszeit.repositories import PlanDraftRepository


@dataclass
class QueriedDraft:
    id: UUID
    creation_date: datetime
    product_name: str
    description: str


@dataclass
class DraftQueryResponse:
    results: List[QueriedDraft]


@inject
@dataclass
class QueryDrafts:
    draft_repository: PlanDraftRepository

    def __call__(
        self,
        company_id: UUID,
    ) -> DraftQueryResponse:
        results = [
            self._draft_to_response_model(draft)
            for draft in self.draft_repository.all_drafts_of_company(company_id)
        ]
        return DraftQueryResponse(results=results)

    def _draft_to_response_model(self, draft: PlanDraft) -> QueriedDraft:
        return QueriedDraft(
            id=draft.id,
            creation_date=draft.creation_date,
            product_name=draft.product_name,
            description=draft.description,
        )
