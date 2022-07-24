from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol, Union

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.plan_summary import PlanSummary
from arbeitszeit.use_cases import CreatePlanDraftRequest, DraftSummarySuccess
from arbeitszeit_web.session import Session


class CreateDraftForm(Protocol):
    def get_prd_name(self) -> str:
        ...

    def get_description(self) -> str:
        ...

    def get_timeframe(self) -> int:
        ...

    def get_prd_unit(self) -> str:
        ...

    def get_prd_amount(self) -> int:
        ...

    def get_costs_p(self) -> Decimal:
        ...

    def get_costs_r(self) -> Decimal:
        ...

    def get_costs_a(self) -> Decimal:
        ...

    def get_productive_or_public(self) -> str:
        ...

    def get_action(self) -> str:
        ...


@dataclass
class PrefilledDraftDataController:
    session: Session

    def import_form_data(self, draft_form: CreateDraftForm) -> CreatePlanDraftRequest:
        planner = self.session.get_current_user()
        assert planner
        return CreatePlanDraftRequest(
            costs=ProductionCosts(
                labour_cost=draft_form.get_costs_a(),
                resource_cost=draft_form.get_costs_r(),
                means_cost=draft_form.get_costs_p(),
            ),
            product_name=draft_form.get_prd_name(),
            production_unit=draft_form.get_prd_unit(),
            production_amount=draft_form.get_prd_amount(),
            description=draft_form.get_description(),
            timeframe_in_days=draft_form.get_timeframe(),
            is_public_service=True
            if draft_form.get_productive_or_public() == "public"
            else False,
            planner=planner,
        )


@dataclass
class GetPrefilledDraftDataPresenter:
    @dataclass
    class PrefilledDraftData:
        prd_name: str
        description: str
        timeframe: int
        prd_unit: str
        prd_amount: int
        costs_p: Decimal
        costs_r: Decimal
        costs_a: Decimal
        productive_or_public: str
        action: str

    @dataclass
    class ViewModel:
        prefilled_draft_data: GetPrefilledDraftDataPresenter.PrefilledDraftData
        self_approve_plan_url: str
        save_draft_url: str
        cancel_url: str

    def show_prefilled_draft_data(
        self,
        summary_data: Union[PlanSummary, DraftSummarySuccess],
    ) -> ViewModel:
        prefilled_data = self.PrefilledDraftData(
            prd_name=summary_data.product_name,
            description=summary_data.description,
            timeframe=summary_data.timeframe,
            prd_unit=summary_data.production_unit,
            prd_amount=summary_data.amount,
            costs_p=summary_data.means_cost,
            costs_r=summary_data.resources_cost,
            costs_a=summary_data.labour_cost,
            productive_or_public="public"
            if summary_data.is_public_service
            else "productive",
            action="",
        )
        return self.ViewModel(
            prefilled_draft_data=prefilled_data,
            self_approve_plan_url="/company/create_draft",
            save_draft_url="/company/create_draft",
            cancel_url="/company/create_draft",
        )
