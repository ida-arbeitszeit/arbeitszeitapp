from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.email_notifications import EmailSender, RejectedPlanNotification
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class RejectPlanInteractor:
    @dataclass
    class Request:
        plan: UUID

    @dataclass
    class Response:
        is_plan_rejected: bool = True

    database_gateway: DatabaseGateway
    datetime_service: DatetimeService
    email_sender: EmailSender

    def reject_plan(self, request: Request) -> Response:
        now = self.datetime_service.now()
        matching_plans = self.database_gateway.get_plans().with_id(request.plan)
        plan = matching_plans.first()
        assert plan
        planner = self.database_gateway.get_companies().with_id(plan.planner).first()
        assert planner
        if plan.is_rejected:
            return self.Response(is_plan_rejected=False)
        matching_plans.update().set_rejection_date(now).perform()
        email_address_from_planner = (
            self.database_gateway.get_email_addresses()
            .that_belong_to_company(planner.id)
            .first()
        )
        assert email_address_from_planner
        self.email_sender.send_email(
            RejectedPlanNotification(
                planner_email_address=email_address_from_planner.address,
                planning_company_name=planner.name,
                plan_id=plan.id,
                product_name=plan.prd_name,
            )
        )
        return self.Response()
