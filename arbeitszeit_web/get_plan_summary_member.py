from dataclasses import asdict, dataclass
from typing import Any, Dict

from arbeitszeit.use_cases.get_plan_summary_member import GetPlanSummaryMember
from arbeitszeit_web.formatters.plan_summary_formatter import (
    PlanSummaryFormatter,
    PlanSummaryWeb,
)
from arbeitszeit_web.url_index import PayConsumerProductUrlIndex

from .translator import Translator


@dataclass
class GetPlanSummaryViewModel:
    summary: PlanSummaryWeb
    pay_product_url: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GetPlanSummarySuccessPresenter:
    trans: Translator
    plan_summary_service: PlanSummaryFormatter
    url_index: PayConsumerProductUrlIndex

    def present(
        self, response: GetPlanSummaryMember.Success
    ) -> GetPlanSummaryViewModel:
        return GetPlanSummaryViewModel(
            summary=self.plan_summary_service.format_plan_summary(
                response.plan_summary
            ),
            pay_product_url=self.url_index.get_pay_consumer_product_url(
                amount=1, plan_id=response.plan_summary.plan_id
            ),
        )
