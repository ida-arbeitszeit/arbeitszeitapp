from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional, Protocol, Tuple

from arbeitszeit.plan_summary import BusinessPlanSummary
from arbeitszeit_web.url_index import CompanySummaryUrlIndex, CoopSummaryUrlIndex

from .translator import Translator


@dataclass
class PlanSummary:
    plan_id: Tuple[str, str]
    is_active: Tuple[str, str]
    planner: Tuple[str, str, str, str]
    product_name: Tuple[str, str]
    description: Tuple[str, List[str]]
    timeframe: Tuple[str, str]
    production_unit: Tuple[str, str]
    amount: Tuple[str, str]
    means_cost: Tuple[str, str]
    resources_cost: Tuple[str, str]
    labour_cost: Tuple[str, str]
    type_of_plan: Tuple[str, str]
    price_per_unit: Tuple[str, str, bool, Optional[str]]
    is_available: Tuple[str, str]


class PlanSummaryService(Protocol):
    def get_plan_summary_member(self, plan_summary: BusinessPlanSummary) -> PlanSummary:
        ...


@dataclass
class PlanSummaryServiceImpl:
    coop_url_index: CoopSummaryUrlIndex
    company_url_index: CompanySummaryUrlIndex
    trans: Translator

    def get_plan_summary_member(self, plan_summary: BusinessPlanSummary) -> PlanSummary:
        return PlanSummary(
            plan_id=("Plan-ID", str(plan_summary.plan_id)),
            is_active=("Status", "Aktiv" if plan_summary.is_active else "Inaktiv"),
            planner=(
                self.trans.gettext("Planning company"),
                str(plan_summary.planner_id),
                self.company_url_index.get_company_summary_url(plan_summary.planner_id),
                plan_summary.planner_name,
            ),
            product_name=(
                self.trans.gettext("Name of product"),
                plan_summary.product_name,
            ),
            description=(
                self.trans.gettext("Description of product"),
                plan_summary.description.splitlines(),
            ),
            timeframe=("Planungszeitraum (Tage)", str(plan_summary.timeframe)),
            production_unit=("Kleinste Abgabeeinheit", plan_summary.production_unit),
            amount=("Menge", str(plan_summary.amount)),
            means_cost=("Kosten für Produktionsmittel", str(plan_summary.means_cost)),
            resources_cost=(
                "Kosten für Roh- und Hilfststoffe",
                str(plan_summary.resources_cost),
            ),
            labour_cost=("Arbeitsstunden", str(plan_summary.labour_cost)),
            type_of_plan=(
                "Art des Plans",
                "Öffentlich" if plan_summary.is_public_service else "Produktiv",
            ),
            price_per_unit=(
                "Preis (pro Einheit)",
                self._format_price(plan_summary.price_per_unit),
                plan_summary.is_cooperating,
                self.coop_url_index.get_coop_summary_url(plan_summary.cooperation)
                if plan_summary.cooperation
                else None,
            ),
            is_available=(
                "Produkt aktuell verfügbar",
                "Ja" if plan_summary.is_available else "Nein",
            ),
        )

    def _format_price(self, price_per_unit: Decimal) -> str:
        return f"{round(price_per_unit, 2)}"
