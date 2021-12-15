from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from arbeitszeit.use_cases.get_plan_summary import PlanSummarySuccess

from .url_index import CoopSummaryUrlIndex


@dataclass
class GetPlanSummaryViewModel:
    plan_id: Tuple[str, str]
    is_active: Tuple[str, str]
    planner_id: Tuple[str, str]
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

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GetPlanSummarySuccessPresenter:
    coop_url_index: CoopSummaryUrlIndex

    def present(self, response: PlanSummarySuccess) -> GetPlanSummaryViewModel:
        return GetPlanSummaryViewModel(
            plan_id=("Plan-ID", str(response.plan_id)),
            is_active=("Status", "Aktiv" if response.is_active else "Inaktiv"),
            planner_id=("Planender Betrieb", str(response.planner_id)),
            product_name=("Name des Produkts", response.product_name),
            description=(
                "Beschreibung des Produkts",
                response.description.splitlines(),
            ),
            timeframe=("Planungszeitraum (Tage)", str(response.timeframe)),
            production_unit=("Kleinste Abgabeeinheit", response.production_unit),
            amount=("Menge", str(response.amount)),
            means_cost=("Kosten für Produktionsmittel", str(response.means_cost)),
            resources_cost=(
                "Kosten für Roh- und Hilfststoffe",
                str(response.resources_cost),
            ),
            labour_cost=("Arbeitsstunden", str(response.labour_cost)),
            type_of_plan=(
                "Art des Plans",
                "Öffentlich" if response.is_public_service else "Produktiv",
            ),
            price_per_unit=(
                "Preis (pro Einheit)",
                self.__format_price(response.price_per_unit),
                response.is_cooperating,
                self.coop_url_index.get_coop_summary_url(response.cooperation)
                if response.cooperation
                else None,
            ),
            is_available=(
                "Produkt aktuell verfügbar",
                "Ja" if response.is_available else "Nein",
            ),
        )

    def __format_price(self, price_per_unit: Decimal) -> str:
        return f"{round(price_per_unit, 2)}"
