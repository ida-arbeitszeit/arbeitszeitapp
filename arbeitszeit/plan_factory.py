from datetime import datetime
from decimal import Decimal

from arbeitszeit.entities import Plan, Company, SocialAccounting


class PlanFactory:
    def create_plan(
        self,
        id: int,
        plan_creation_date: datetime,
        planner: Company,
        costs_p: Decimal,
        costs_r: Decimal,
        costs_a: Decimal,
        prd_name: str,
        prd_unit: str,
        prd_amount: int,
        description: str,
        timeframe: int,
        social_accounting: SocialAccounting,
        approved: bool,
        approval_date: datetime,
        approval_reason: str,
    ) -> Plan:
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
