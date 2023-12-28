from dataclasses import dataclass

from arbeitszeit.records import ProductionCosts
from arbeitszeit.use_cases.create_plan_draft import Request
from arbeitszeit_web.forms import DraftForm
from arbeitszeit_web.session import Session


@dataclass
class CreateDraftController:
    session: Session

    def import_form_data(self, draft_form: DraftForm) -> Request:
        planner = self.session.get_current_user()
        assert planner
        return Request(
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
