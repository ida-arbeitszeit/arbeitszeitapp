from datetime import datetime
from typing import Union

from arbeitszeit.entities import PlanApproval, Plan, SocialAccounting


class ApprovalFactory:
    def create_plan_approval(
        approval_date: datetime,
        social_accounting: SocialAccounting,
        plan: Plan,
        approved: bool,
        reason: Union[str, None],
    ) -> PlanApproval:
        return PlanApproval(
            approval_date=approval_date,
            social_accounting=social_accounting,
            plan=plan,
            approved=approved,
            reason=reason,
        )
