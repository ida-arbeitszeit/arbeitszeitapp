from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.interactors.revoke_plan_filing import RevokePlanFilingInteractor
from arbeitszeit_web.session import Session


@dataclass
class RevokePlanFilingController:
    session: Session

    def create_request(self, plan_id: UUID) -> RevokePlanFilingInteractor.Request:
        requester = self.session.get_current_user()
        assert requester
        return RevokePlanFilingInteractor.Request(plan=plan_id, requester=requester)
