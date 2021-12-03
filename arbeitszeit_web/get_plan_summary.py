from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Tuple

from arbeitszeit.use_cases.get_plan_summary import PlanSummarySuccess


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
    price_per_unit: Tuple[str, str, bool]
    is_available: Tuple[str, str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GetPlanSummarySuccessPresenter:
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
                str(response.price_per_unit),
                response.is_cooperating,
            ),
            is_available=(
                "Produkt aktuell verfügbar",
                "Ja" if response.is_available else "Nein",
            ),
        )
