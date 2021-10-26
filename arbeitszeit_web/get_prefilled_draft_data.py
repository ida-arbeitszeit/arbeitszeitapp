from dataclasses import dataclass
from typing import Union

from arbeitszeit.use_cases import DraftSummarySuccess, PlanSummarySuccess


@dataclass
class PrefilledDraftData:
    from_expired_plan: bool
    product_name: str
    description: str
    timeframe: str
    production_unit: str
    amount: str
    means_cost: str
    resources_cost: str
    labour_cost: str
    is_public_service: bool


class GetPrefilledDraftData:
    def __call__(
        self,
        summary_data: Union[PlanSummarySuccess, DraftSummarySuccess],
        from_expired_plan: bool,
    ) -> PrefilledDraftData:
        return PrefilledDraftData(
            from_expired_plan=True if from_expired_plan else False,
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
