from dataclasses import dataclass

from arbeitszeit.interactors.get_plan_details import GetPlanDetailsInteractor
from arbeitszeit_web.formatters.plan_details_formatter import (
    PlanDetailsFormatter,
    PlanDetailsWeb,
)
from arbeitszeit_web.url_index import UrlIndex

from ...translator import Translator


@dataclass
class GetPlanDetailsMemberViewModel:
    details: PlanDetailsWeb
    register_private_consumption_url: str


@dataclass
class GetPlanDetailsMemberMemberPresenter:
    trans: Translator
    plan_details_service: PlanDetailsFormatter
    url_index: UrlIndex

    def present(
        self, response: GetPlanDetailsInteractor.Response
    ) -> GetPlanDetailsMemberViewModel:
        return GetPlanDetailsMemberViewModel(
            details=self.plan_details_service.format_plan_details(
                response.plan_details
            ),
            register_private_consumption_url=self.url_index.get_register_private_consumption_url(
                amount=None, plan_id=response.plan_details.plan_id
            ),
        )
