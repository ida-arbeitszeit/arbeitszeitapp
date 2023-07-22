from dataclasses import asdict, dataclass
from typing import Any, Dict

from arbeitszeit.use_cases.get_plan_details import GetPlanDetailsUseCase
from arbeitszeit_web.formatters.plan_details_formatter import (
    PlanDetailsFormatter,
    PlanDetailsWeb,
)
from arbeitszeit_web.url_index import UrlIndex

from ...translator import Translator


@dataclass
class GetPlanDetailsMemberViewModel:
    details: PlanDetailsWeb
    pay_product_url: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GetPlanDetailsMemberMemberPresenter:
    trans: Translator
    plan_details_service: PlanDetailsFormatter
    url_index: UrlIndex

    def present(
        self, response: GetPlanDetailsUseCase.Response
    ) -> GetPlanDetailsMemberViewModel:
        return GetPlanDetailsMemberViewModel(
            details=self.plan_details_service.format_plan_details(
                response.plan_details
            ),
            pay_product_url=self.url_index.get_pay_consumer_product_url(
                amount=None, plan_id=response.plan_details.plan_id
            ),
        )
