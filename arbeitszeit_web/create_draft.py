from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Union

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.plan_summary import PlanSummary
from arbeitszeit.use_cases import CreatePlanDraftRequest, DraftSummarySuccess
from arbeitszeit_web.forms import DraftForm
from arbeitszeit_web.session import Session


@dataclass
class CreateDraftController:
    session: Session

    def import_form_data(self, draft_form: DraftForm) -> CreatePlanDraftRequest:
        planner = self.session.get_current_user()
        assert planner
        return CreatePlanDraftRequest(
            costs=ProductionCosts(
                labour_cost=draft_form.labour_cost_field().get_value(),
                resource_cost=draft_form.resource_cost_field().get_value(),
                means_cost=draft_form.means_cost_field().get_value(),
            ),
            product_name=draft_form.product_name_field().get_value(),
            production_unit=draft_form.unit_of_distribution_field().get_value(),
            production_amount=draft_form.amount_field().get_value(),
            description=draft_form.description_field().get_value(),
            timeframe_in_days=draft_form.timeframe_field().get_value(),
            is_public_service=draft_form.is_public_service_field().get_value(),
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
        is_public_service: bool
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
            is_public_service=summary_data.is_public_service,
            action="",
        )
        return self.ViewModel(
            prefilled_draft_data=prefilled_data,
            self_approve_plan_url="/company/create_draft",
            save_draft_url="/company/create_draft",
            cancel_url="/company/create_draft",
        )
