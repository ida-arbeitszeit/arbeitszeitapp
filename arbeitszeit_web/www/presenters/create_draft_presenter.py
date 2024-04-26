from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union

from arbeitszeit.plan_details import PlanDetails
from arbeitszeit.use_cases.create_plan_draft import Response
from arbeitszeit.use_cases.get_draft_details import DraftDetailsSuccess
from arbeitszeit_web.forms import DraftForm
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class GetPrefilledDraftDataPresenter:
    @dataclass
    class ViewModel:
        save_draft_url: str
        cancel_url: str

    url_index: UrlIndex

    def show_prefilled_draft_data(
        self, draft_data: Union[PlanDetails, DraftDetailsSuccess], form: DraftForm
    ) -> ViewModel:
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
            save_draft_url=self.url_index.get_create_draft_url(),
            cancel_url=self.url_index.get_my_plans_url(),
        )


@dataclass
class CreateDraftPresenter:
    @dataclass
    class ViewModel:
        redirect_url: Optional[str]

    url_index: UrlIndex
    notifier: Notifier
    translator: Translator

    def present_plan_creation(self, response: Response) -> ViewModel:
        redirect_url: Optional[str]
        if response.draft_id is None:
            redirect_url = None
        else:
            redirect_url = self.url_index.get_my_plan_drafts_url()
            self.notifier.display_info(
                self.translator.gettext("Plan draft successfully created")
            )
        return self.ViewModel(redirect_url=redirect_url)
