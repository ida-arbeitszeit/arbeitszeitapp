from uuid import UUID

from arbeitszeit.interactors.approve_plan import ApprovePlanInteractor as Interactor


class ApprovePlanController:
    def approve_plan(self, plan: UUID) -> Interactor.Request:
        return Interactor.Request(plan=plan)
