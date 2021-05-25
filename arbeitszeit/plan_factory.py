from datetime import datetime
from decimal import Decimal
from typing import Tuple

from arbeitszeit.entities import Plan, Company, SocialAccounting


class PlanFactory:
    def create_plan(
        self,
        id: int,
        plan_creation_date: datetime,
        planner: Company,
        plan_details: Tuple[Decimal, Decimal, Decimal, str, str, int, str, int],
        social_accounting: SocialAccounting,
        approved: bool,
        approval_date: datetime,
        approval_reason: str,
    ) -> Plan:
        (
            costs_p,
            costs_r,
            costs_a,
            prd_name,
            prd_unit,
            prd_amount,
            description,
            timeframe,
        ) = plan_details
        return Plan(
            id=id,
            plan_creation_date=plan_creation_date,
            planner=planner,
            costs_p=costs_p,
            costs_r=costs_r,
            costs_a=costs_a,
            prd_name=prd_name,
            prd_unit=prd_unit,
            prd_amount=prd_amount,
            description=description,
            timeframe=timeframe,
            social_accounting=social_accounting,
            approved=approved,
            approval_date=approval_date,
            approval_reason=approval_reason,
        )
