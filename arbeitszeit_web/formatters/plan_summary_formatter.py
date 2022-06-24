from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional, Tuple

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.plan_summary import PlanSummary
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import CompanySummaryUrlIndex, CoopSummaryUrlIndex


@dataclass
class PlanSummaryWeb:
    plan_id: Tuple[str, str]
    activity_string: Tuple[str, str]
    planner: Tuple[str, str, str, str]
    product_name: Tuple[str, str]
    description: Tuple[str, List[str]]
    timeframe: Tuple[str, str]
    active_days: str
    production_unit: Tuple[str, str]
    amount: Tuple[str, str]
    means_cost: Tuple[str, str]
    resources_cost: Tuple[str, str]
    labour_cost: Tuple[str, str]
    type_of_plan: Tuple[str, str]
    price_per_unit: Tuple[str, str, bool, Optional[str]]
    availability_string: Tuple[str, str]
    creation_date: str
    approval_date: str
    expiration_date: str


@dataclass
class PlanSummaryFormatter:
    coop_url_index: CoopSummaryUrlIndex
    company_url_index: CompanySummaryUrlIndex
    translator: Translator
    datetime_service: DatetimeService

    def format_plan_summary(self, plan_summary: PlanSummary) -> PlanSummaryWeb:
        return PlanSummaryWeb(
            plan_id=(self.translator.gettext("Plan ID"), str(plan_summary.plan_id)),
            activity_string=(
                self.translator.gettext("Status"),
                self.translator.gettext("Active")
                if plan_summary.is_active
                else self.translator.gettext("Inactive"),
            ),
            planner=(
                self.translator.gettext("Planning company"),
                str(plan_summary.planner_id),
                self.company_url_index.get_company_summary_url(plan_summary.planner_id),
                plan_summary.planner_name,
            ),
            product_name=(
                self.translator.gettext("Name of product"),
                plan_summary.product_name,
            ),
            description=(
                self.translator.gettext("Description of product"),
                plan_summary.description.splitlines(),
            ),
            timeframe=(
                self.translator.gettext("Planning timeframe (days)"),
                str(plan_summary.timeframe),
            ),
            active_days=str(plan_summary.active_days),
            production_unit=(
                self.translator.gettext("Smallest delivery unit"),
                plan_summary.production_unit,
            ),
            amount=(self.translator.gettext("Amount"), str(plan_summary.amount)),
            means_cost=(
                self.translator.gettext("Costs for fixed means of production"),
                str(plan_summary.means_cost),
            ),
            resources_cost=(
                self.translator.gettext("Costs for liquid means of production"),
                str(plan_summary.resources_cost),
            ),
            labour_cost=(
                self.translator.gettext("Costs for work"),
                str(plan_summary.labour_cost),
            ),
            type_of_plan=(
                self.translator.gettext("Type"),
                self.translator.gettext("Public")
                if plan_summary.is_public_service
                else self.translator.gettext("Productive"),
            ),
            price_per_unit=(
                self.translator.gettext("Price (per unit)"),
                self._format_price(plan_summary.price_per_unit),
                plan_summary.is_cooperating,
                self.coop_url_index.get_coop_summary_url(plan_summary.cooperation)
                if plan_summary.cooperation
                else None,
            ),
            availability_string=(
                self.translator.gettext("Product currently available"),
                self.translator.gettext("Yes")
                if plan_summary.is_available
                else self.translator.gettext("No"),
            ),
            creation_date=self.datetime_service.format_datetime(
                date=plan_summary.creation_date,
                zone="Europe/Berlin",
                fmt="%d.%m.%Y %H:%M",
            ),
            approval_date=self.datetime_service.format_datetime(
                date=plan_summary.approval_date,
                zone="Europe/Berlin",
                fmt="%d.%m.%Y %H:%M",
            )
            if plan_summary.approval_date
            else "-",
            expiration_date=self.datetime_service.format_datetime(
                date=plan_summary.expiration_date,
                zone="Europe/Berlin",
                fmt="%d.%m.%Y %H:%M",
            )
            if plan_summary.expiration_date
            else "-",
        )

    def _format_price(self, price_per_unit: Decimal) -> str:
        return f"{round(price_per_unit, 2)}"
