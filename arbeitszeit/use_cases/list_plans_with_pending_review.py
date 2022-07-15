from __future__ import annotations

from dataclasses import dataclass
from typing import List


class ListPlansWithPendingReviewUseCase:
    class Request:
        pass

    class Plan:
        pass

    @dataclass
    class Response:
        plans: List[ListPlansWithPendingReviewUseCase.Plan]

    def list_plans_with_pending_review(self, request: Request) -> Response:
        return self.Response(plans=[])
