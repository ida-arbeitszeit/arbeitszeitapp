from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional, Tuple

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.plan_details import PlanDetails
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class PlanDetailsWeb:
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
    labour_cost_per_unit: Optional[Tuple[str, str]]
    creation_date: str
    approval_date: str
    expiration_date: str


@dataclass
class PlanDetailsFormatter:
    url_index: UrlIndex
    translator: Translator
    datetime_service: DatetimeService

    def format_plan_details(self, plan_details: PlanDetails) -> PlanDetailsWeb:
        return PlanDetailsWeb(
            plan_id=(self.translator.gettext("Plan ID"), str(plan_details.plan_id)),
            activity_string=(
                self.translator.gettext("Status"),
                self.translator.gettext("Active")
                if plan_details.is_active
                else self.translator.gettext("Inactive"),
            ),
            planner=(
                self.translator.gettext("Planning company"),
                str(plan_details.planner_id),
                self.url_index.get_company_summary_url(
                    company_id=plan_details.planner_id,
                ),
                plan_details.planner_name,
            ),
            product_name=(
                self.translator.gettext("Name of product"),
                plan_details.product_name,
            ),
            description=(
                self.translator.gettext("Description of product"),
                plan_details.description.splitlines(),
            ),
            timeframe=(
                self.translator.gettext("Planning timeframe (days)"),
                str(plan_details.timeframe),
            ),
            active_days=str(plan_details.active_days),
            production_unit=(
                self.translator.gettext("Smallest delivery unit"),
                plan_details.production_unit,
            ),
            amount=(self.translator.gettext("Amount"), str(plan_details.amount)),
            means_cost=(
                self.translator.gettext("Costs for fixed means of production"),
                str(plan_details.means_cost),
            ),
            resources_cost=(
                self.translator.gettext("Costs for liquid means of production"),
                str(plan_details.resources_cost),
            ),
            labour_cost=(
                self.translator.gettext("Costs for work"),
                str(plan_details.labour_cost),
            ),
            type_of_plan=(
                self.translator.gettext("Type"),
                self.translator.gettext("Public")
                if plan_details.is_public_service
                else self.translator.gettext("Productive"),
            ),
            price_per_unit=(
                self.translator.gettext("Price (per unit)"),
                self._format_price(plan_details.price_per_unit),
                plan_details.is_cooperating,
                self.url_index.get_coop_summary_url(coop_id=plan_details.cooperation)
                if plan_details.cooperation
                else None,
            ),
            labour_cost_per_unit=(
                self.translator.gettext("Labour (per unit)"),
                self._format_price(plan_details.labour_cost_per_unit),
            ),
            creation_date=self.datetime_service.format_datetime(
                date=plan_details.creation_date,
                zone="Europe/Berlin",
                fmt="%d.%m.%Y %H:%M",
            ),
            approval_date=self.datetime_service.format_datetime(
                date=plan_details.approval_date,
                zone="Europe/Berlin",
                fmt="%d.%m.%Y %H:%M",
            )
            if plan_details.approval_date
            else "-",
            expiration_date=self.datetime_service.format_datetime(
                date=plan_details.expiration_date,
                zone="Europe/Berlin",
                fmt="%d.%m.%Y %H:%M",
            )
            if plan_details.expiration_date
            else "-",
        )

    def _format_price(self, price_per_unit: Decimal) -> str:
        return f"{round(price_per_unit, 2)}"
