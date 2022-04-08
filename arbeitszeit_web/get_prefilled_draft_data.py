from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol, Union
from uuid import UUID

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.plan_summary import BusinessPlanSummary
from arbeitszeit.use_cases import CreatePlanDraftRequest, DraftSummarySuccess


class CreateDraftForm(Protocol):
    def get_prd_name_string(self) -> str:
        ...

    def get_description_string(self) -> str:
        ...

    def get_timeframe_string(self) -> str:
        ...

    def get_prd_unit_string(self) -> str:
        ...

    def get_prd_amount_string(self) -> str:
        ...

    def get_costs_p_string(self) -> str:
        ...

    def get_costs_r_string(self) -> str:
        ...

    def get_costs_a_string(self) -> str:
        ...

    def get_productive_or_public_string(self) -> str:
        ...

    def get_action_string(self) -> str:
        ...


class PrefilledDraftDataController:
    def import_form_data(
        self, planner: UUID, draft_form: CreateDraftForm
    ) -> CreatePlanDraftRequest:
        labour_costs = Decimal(draft_form.get_costs_a_string())
        resource_cost = Decimal(draft_form.get_costs_r_string())
        means_cost = Decimal(draft_form.get_costs_p_string())
        production_amount = int(draft_form.get_prd_amount_string())
        timeframe_in_days = int(draft_form.get_timeframe_string())
        assert labour_costs >= 0
        assert resource_cost >= 0
        assert means_cost >= 0
        assert production_amount >= 0
        assert timeframe_in_days >= 0
        return CreatePlanDraftRequest(
            costs=ProductionCosts(
                labour_cost=labour_costs,
                resource_cost=resource_cost,
                means_cost=means_cost,
            ),
            product_name=draft_form.get_prd_name_string(),
            production_unit=draft_form.get_prd_unit_string(),
            production_amount=production_amount,
            description=draft_form.get_description_string(),
            timeframe_in_days=timeframe_in_days,
            is_public_service=True
            if draft_form.get_productive_or_public_string() == "public"
            else False,
            planner=planner,
        )


@dataclass
class PrefilledDraftData:
    product_name: str
    description: str
    timeframe: str
    production_unit: str
    amount: str
    means_cost: str
    resources_cost: str
    labour_cost: str
    is_public_service: bool


class GetPrefilledDraftDataPresenter:
    def present(
        self, summary_data: Union[BusinessPlanSummary, DraftSummarySuccess]
    ) -> PrefilledDraftData:
        return PrefilledDraftData(
            product_name=summary_data.product_name,
            description=summary_data.description,
            timeframe=f"{summary_data.timeframe}",
            production_unit=summary_data.production_unit,
            amount=f"{summary_data.amount}",
            means_cost=f"{summary_data.means_cost}",
            resources_cost=f"{summary_data.resources_cost}",
            labour_cost=f"{summary_data.labour_cost}",
            is_public_service=summary_data.is_public_service,
        )
