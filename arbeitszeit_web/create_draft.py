from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.plan_summary import PlanSummary
from arbeitszeit.use_cases.create_plan_draft import (
    CreatePlanDraftRequest,
    CreatePlanDraftResponse,
)
from arbeitszeit.use_cases.get_draft_summary import DraftSummarySuccess
from arbeitszeit_web.forms import DraftForm
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


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
    class ViewModel:
        load_draft_url: str
        save_draft_url: str
        cancel_url: str

    url_index: UrlIndex

    def show_prefilled_draft_data(
        self, summary_data: Union[PlanSummary, DraftSummarySuccess], form: DraftForm
    ) -> ViewModel:
        form.product_name_field().set_value(summary_data.product_name)
        form.description_field().set_value(summary_data.description)
        form.timeframe_field().set_value(summary_data.timeframe)
        form.unit_of_distribution_field().set_value(summary_data.production_unit)
        form.amount_field().set_value(summary_data.amount)
        form.means_cost_field().set_value(summary_data.means_cost)
        form.resource_cost_field().set_value(summary_data.resources_cost)
        form.labour_cost_field().set_value(summary_data.labour_cost)
        form.is_public_service_field().set_value(summary_data.is_public_service)
        return self.ViewModel(
            load_draft_url=self.url_index.get_my_plan_drafts_url(),
            save_draft_url=self.url_index.get_create_draft_url(),
            cancel_url=self.url_index.get_create_draft_url(),
        )


@dataclass
class CreateDraftPresenter:
    @dataclass
    class ViewModel:
        redirect_url: Optional[str]

    url_index: UrlIndex
    notifier: Notifier
    translator: Translator

    def present_plan_creation(self, response: CreatePlanDraftResponse) -> ViewModel:
        redirect_url: Optional[str]
        if response.draft_id is None:
            redirect_url = None
        else:
            redirect_url = self.url_index.get_my_plan_drafts_url()
            self.notifier.display_info(
                self.translator.gettext("Plan draft successfully created")
            )
        return self.ViewModel(redirect_url=redirect_url)
