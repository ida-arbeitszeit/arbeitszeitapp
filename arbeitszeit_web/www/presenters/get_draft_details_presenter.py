from __future__ import annotations

from dataclasses import dataclass

from arbeitszeit.plan_details import PlanDetails
from arbeitszeit.use_cases.get_draft_details import DraftDetailsSuccess
from arbeitszeit_web.forms import DraftForm
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class GetDraftDetailsPresenter:
    @dataclass
    class ViewModel:
        save_draft_url: str
        cancel_url: str

    url_index: UrlIndex

    def present_draft_details(
        self, draft_data: PlanDetails | DraftDetailsSuccess, form: DraftForm
    ) -> ViewModel:
        if isinstance(draft_data, PlanDetails):
            draft_id = draft_data.plan_id
        else:
            draft_id = draft_data.draft_id
        form.product_name_field().set_value(draft_data.product_name)
        form.description_field().set_value(draft_data.description)
        form.timeframe_field().set_value(draft_data.timeframe)
        form.unit_of_distribution_field().set_value(draft_data.production_unit)
        form.amount_field().set_value(draft_data.amount)
        form.means_cost_field().set_value(draft_data.means_cost)
        form.resource_cost_field().set_value(draft_data.resources_cost)
        form.labour_cost_field().set_value(draft_data.labour_cost)
        form.is_public_service_field().set_value(draft_data.is_public_service)
        return self.ViewModel(
            save_draft_url=self.url_index.get_draft_details_url(draft_id),
            cancel_url=self.url_index.get_my_plans_url(),
        )
