from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from arbeitszeit.entities import PurposesOfPurchases
from arbeitszeit.use_cases.pay_means_of_production import PayMeansOfProductionRequest
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session


class PayMeansOfProductionForm(Protocol):
    def get_plan_id_field(self) -> UUID:
        ...

    def get_amount_field(self) -> int:
        ...

    def get_category_field(self) -> str:
        ...


@dataclass
class PayMeansOfProductionController:
    session: Session
    request: Request

    def process_input_data(
        self, form: PayMeansOfProductionForm
    ) -> PayMeansOfProductionRequest:
        buyer = self.session.get_current_user()
        assert buyer
        plan = form.get_plan_id_field()
        amount = form.get_amount_field()
        purpose = (
            PurposesOfPurchases.means_of_prod
            if form.get_category_field() == "Fixed"
            else PurposesOfPurchases.raw_materials
        )
        return PayMeansOfProductionRequest(buyer, plan, amount, purpose)
