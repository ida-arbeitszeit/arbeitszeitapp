from __future__ import annotations

from dataclasses import dataclass

from arbeitszeit.interactors.get_draft_details import DraftDetailsSuccess
from arbeitszeit_web.forms import DraftForm
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class GetDraftDetailsPresenter:
    @dataclass
    class ViewModel:
        cancel_url: str
        form: DraftForm

    url_index: UrlIndex

    def present_draft_details(self, draft_data: DraftDetailsSuccess) -> ViewModel:
        form = DraftForm(
            product_name_value=draft_data.product_name,
            description_value=draft_data.description,
            timeframe_value=str(draft_data.timeframe),
            unit_of_distribution_value=draft_data.production_unit,
            amount_value=str(draft_data.amount),
            means_cost_value=str(draft_data.means_cost),
            resource_cost_value=str(draft_data.resources_cost),
            labour_cost_value=str(draft_data.labour_cost),
            is_public_plan_value="on" if draft_data.is_public_service else "",
        )
        return self.ViewModel(
            cancel_url=self.url_index.get_my_plans_url(),
            form=form,
        )
