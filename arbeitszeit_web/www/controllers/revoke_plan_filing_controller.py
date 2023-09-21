from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.use_cases.revoke_plan_filing import RevokePlanFilingUseCase
from arbeitszeit_web.session import Session


@dataclass
class RevokePlanFilingController:
    session: Session

    def create_request(self, plan_id: UUID) -> RevokePlanFilingUseCase.Request:
        requester = self.session.get_current_user()
        assert requester
        return RevokePlanFilingUseCase.Request(plan=plan_id, requester=requester)
