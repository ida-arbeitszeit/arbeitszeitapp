from uuid import UUID

from arbeitszeit.use_cases.approve_plan import ApprovePlanUseCase as UseCase


class ApprovePlanController:
    def approve_plan(self, plan: UUID) -> UseCase.Request:
        return UseCase.Request(plan=plan)
