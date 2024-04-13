from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from arbeitszeit.control_thresholds import ControlThresholds
from arbeitszeit.use_cases.get_company_summary import (
    GetCompanySummarySuccess,
    PlanDetails,
    Supplier,
)
from arbeitszeit_web.formatters.datetime_formatter import DatetimeFormatter
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex, UserUrlIndex


@dataclass
class Deviation:
    percentage: str
    is_critical: bool


@dataclass
class PlanDetailsWeb:
    id: str
    name: str
    url: str
    status: str
    sales_volume: str
    sales_balance: str
    deviation_relative: Deviation


@dataclass
class SuppliersWeb:
    company_url: str
    company_name: str
    volume_of_sales: str


@dataclass
class GetCompanySummaryViewModel:
    id: str
    name: str
    email: str
    registered_on: str
    expectations: List[str]
    account_balances: List[str]
    deviations_relative: List[Deviation]
    plan_details: List[PlanDetailsWeb]
    suppliers_ordered_by_volume: List[SuppliersWeb]
    show_suppliers: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GetCompanySummarySuccessPresenter:
    user_url_index: UserUrlIndex
    translator: Translator
    url_index: UrlIndex
    control_thresholds: ControlThresholds
    datetime_formatter: DatetimeFormatter

    def present(
        self, use_case_response: GetCompanySummarySuccess
    ) -> GetCompanySummaryViewModel:
        suppliers_ordered_by_volume = self._get_suppliers(
            use_case_response.suppliers_ordered_by_volume
        )
        return GetCompanySummaryViewModel(
            id=str(use_case_response.id),
            name=use_case_response.name,
            email=use_case_response.email,
            registered_on=self.datetime_formatter.format_datetime(
                use_case_response.registered_on, zone="Europe/Berlin", fmt="%d.%m.%Y"
            ),
            expectations=[
                "%(num).2f" % dict(num=use_case_response.expectations.means),
                "%(num).2f" % dict(num=use_case_response.expectations.raw_material),
                "%(num).2f" % dict(num=use_case_response.expectations.work),
                "%(num).2f" % dict(num=use_case_response.expectations.product),
            ],
            account_balances=[
                "%(num).2f" % dict(num=use_case_response.account_balances.means),
                "%(num).2f" % dict(num=use_case_response.account_balances.raw_material),
                "%(num).2f" % dict(num=use_case_response.account_balances.work),
                "%(num).2f" % dict(num=use_case_response.account_balances.product),
            ],
            deviations_relative=[
                Deviation(
                    percentage="%(num).0f"
                    % dict(num=use_case_response.deviations_relative[i]),
                    is_critical=abs(use_case_response.deviations_relative[i])
                    > self.control_thresholds.get_acceptable_relative_account_deviation(),
                )
                for i in range(len(use_case_response.deviations_relative))
            ],
            plan_details=[
                self._get_plan_details(plan) for plan in use_case_response.plan_details
            ],
            suppliers_ordered_by_volume=suppliers_ordered_by_volume,
            show_suppliers=bool(suppliers_ordered_by_volume),
        )

    def _get_plan_details(self, plan_details: PlanDetails) -> PlanDetailsWeb:
        return PlanDetailsWeb(
            id=str(plan_details.id),
            name=plan_details.name,
            url=self.user_url_index.get_plan_details_url(
                plan_details.id,
            ),
            status=(
                self.translator.gettext("Active")
                if plan_details.is_active
                else self.translator.gettext("Inactive")
            ),
            sales_volume=f"{round(plan_details.sales_volume, 2)}",
            sales_balance=f"{round(plan_details.sales_balance, 2)}",
            deviation_relative=Deviation(
                percentage="%(num).0f" % dict(num=plan_details.deviation_relative),
                is_critical=abs(plan_details.deviation_relative)
                > self.control_thresholds.get_acceptable_relative_account_deviation(),
            ),
        )

    def _get_suppliers(self, suppliers: List[Supplier]) -> List[SuppliersWeb]:
        return [
            SuppliersWeb(
                company_url=self.url_index.get_company_summary_url(
                    company_id=supplier.company_id,
                ),
                company_name=supplier.company_name,
                volume_of_sales=f"{supplier.volume_of_sales:.2f}",
            )
            for supplier in suppliers
        ]
