from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit.accountant_notifications import AccountantNotifier
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class FilePlanWithAccounting:
    @dataclass
    class Request:
        draft_id: UUID
        filing_company: UUID

    @dataclass
    class Response:
        is_plan_successfully_filed: bool
        plan_id: Optional[UUID]

    database_gateway: DatabaseGateway
    datetime_service: DatetimeService
    accountant_notifier: AccountantNotifier

    def file_plan_with_accounting(self, request: Request) -> Response:
        query_result = (
            self.database_gateway.get_plan_drafts()
            .with_id(request.draft_id)
            .joined_with_planner_and_email_address()
            .first()
        )
        if not query_result:
            return self.Response(
                is_plan_successfully_filed=False,
                plan_id=None,
            )
        draft, _, email_address = query_result
        if (
            draft
            and draft.planner == request.filing_company
            and email_address.confirmed_on
        ):
            plan = self.database_gateway.create_plan(
                creation_timestamp=self.datetime_service.now(),
                planner=draft.planner,
                production_costs=draft.production_costs,
                product_name=draft.product_name,
                distribution_unit=draft.unit_of_distribution,
                amount_produced=draft.amount_produced,
                product_description=draft.description,
                duration_in_days=draft.timeframe,
                is_public_service=draft.is_public_service,
            )
            assert plan
            self.database_gateway.get_plan_drafts().with_id(draft.id).delete()
            is_plan_successfully_filed = True
            self.accountant_notifier.notify_all_accountants_about_new_plan(
                product_name=draft.product_name,
                plan_id=plan.id,
            )
        else:
            plan = None
            is_plan_successfully_filed = False
        return self.Response(
            is_plan_successfully_filed=is_plan_successfully_filed,
            plan_id=plan.id if plan else None,
        )
