from dataclasses import dataclass
from typing import Dict, List, Protocol, Union
from uuid import UUID

from arbeitszeit.entities import PurposesOfPurchases
from arbeitszeit.use_cases.pay_means_of_production import PayMeansOfProductionRequest
from arbeitszeit_web.request import Request
from arbeitszeit_web.session import Session


class PayMeansOfProductionForm(Protocol):
    def get_plan_id_field(self) -> str:
        ...

    def get_amount_field(self) -> int:
        ...

    def get_category_field(self) -> str:
        ...

    def validate(self) -> bool:
        ...

    @property
    def errors(self) -> Dict:
        ...


@dataclass
class PayMeansOfProductionController:
    session: Session
    request: Request

    @dataclass
    class MalformedInputData:
        field_messages: Dict[str, List[str]]

    def process_input_data(
        self, form: PayMeansOfProductionForm
    ) -> Union[PayMeansOfProductionRequest, MalformedInputData]:
        if not form.validate():
            return self._handle_invalid_form(form)
        buyer = self.session.get_current_user()
        assert buyer
        plan = UUID(form.get_plan_id_field())
        amount = form.get_amount_field()
        purpose = (
            PurposesOfPurchases.means_of_prod
            if form.get_category_field() == "Fixed"
            else PurposesOfPurchases.raw_materials
        )
        return PayMeansOfProductionRequest(buyer, plan, amount, purpose)

    def _handle_invalid_form(
        self, form: PayMeansOfProductionForm
    ) -> MalformedInputData:
        malformed_data = self.MalformedInputData(field_messages=form.errors)
        return malformed_data
