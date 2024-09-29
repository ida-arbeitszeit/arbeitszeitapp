from dataclasses import dataclass

from arbeitszeit.records import ConsumptionType
from arbeitszeit.use_cases.select_productive_consumption import (
    InvalidPlanResponse,
    NoPlanResponse,
    ValidPlanResponse,
)
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.translator import Translator


@dataclass
class SelectProductiveConsumptionPresenter:
    notifier: Notifier
    translator: Translator

    @dataclass
    class ViewModel:
        valid_plan_selected: bool
        plan_id: str | None
        plan_name: str | None
        plan_description: str | None
        amount: int | None
        is_consumption_of_fixed_means: bool
        status_code: int

    def render_response(
        self, response: NoPlanResponse | InvalidPlanResponse | ValidPlanResponse
    ) -> ViewModel:
        if isinstance(response, NoPlanResponse):
            return self.ViewModel(
                valid_plan_selected=False,
                plan_id=None,
                plan_name=None,
                plan_description=None,
                amount=response.amount,
                is_consumption_of_fixed_means=response.consumption_type
                == ConsumptionType.means_of_prod,
                status_code=200,
            )
        if isinstance(response, InvalidPlanResponse):
            self.notifier.display_warning(
                self.translator.gettext(
                    "The selected plan does not exist or is not active anymore."
                )
            )
            return self.ViewModel(
                valid_plan_selected=False,
                plan_id=None,
                plan_name=None,
                plan_description=None,
                amount=response.amount,
                is_consumption_of_fixed_means=response.consumption_type
                == ConsumptionType.means_of_prod,
                status_code=404,
            )
        assert isinstance(response, ValidPlanResponse)
        return self.ViewModel(
            valid_plan_selected=True,
            plan_id=str(response.plan_id),
            plan_name=response.plan_name,
            plan_description=response.plan_description,
            amount=response.amount,
            is_consumption_of_fixed_means=response.consumption_type
            == ConsumptionType.means_of_prod,
            status_code=200,
        )
