from uuid import UUID

from arbeitszeit.use_cases.reject_plan import RejectPlanUseCase as UseCase


class RejectPlanController:
    def reject_plan(self, plan: UUID) -> UseCase.Request:
        return UseCase.Request(plan=plan)
