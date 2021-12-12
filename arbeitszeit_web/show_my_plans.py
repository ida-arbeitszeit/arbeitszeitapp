from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from arbeitszeit.use_cases.show_my_plans import ShowMyPlansResponse

from .url_index import PlanSummaryUrlIndex


@dataclass
class NonActivePlansRow:
    id: str
    plan_summary_url: str
    prd_name: str
    description: List[str]
    price_per_unit: str
    type_of_plan: str
    plan_creation_date: str


@dataclass
class NonActivePlansTable:
    rows: List[NonActivePlansRow]


@dataclass
class ActivePlansRow:
    id: str
    plan_summary_url: str
    prd_name: str
    description: List[str]
    price_per_unit: str
    type_of_plan: str
    activation_date: str
    expiration_date: str
    expiration_relative: str
    is_available: bool


@dataclass
class ActivePlansTable:
    rows: List[ActivePlansRow]


@dataclass
class ExpiredPlansRow:
    id: str
    plan_summary_url: str
    prd_name: str
    description: List[str]
    price_per_unit: str
    type_of_plan: str
    plan_creation_date: str
    renewed: bool


@dataclass
class ExpiredPlansTable:
    rows: List[ExpiredPlansRow]


@dataclass
class ShowMyPlansViewModel:
    notifications: List[str]
    show_non_active_plans: bool
    non_active_plans: NonActivePlansTable
    show_active_plans: bool
    active_plans: ActivePlansTable
    show_expired_plans: bool
    expired_plans: ExpiredPlansTable

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ShowMyPlansPresenter:
    url_index: PlanSummaryUrlIndex

    def present(self, response: ShowMyPlansResponse) -> ShowMyPlansViewModel:

        if not response.count_all_plans:
            notifications = ["Du hast keine Pläne."]
        else:
            notifications = []
        return ShowMyPlansViewModel(
            notifications=notifications,
            show_non_active_plans=bool(response.non_active_plans),
            non_active_plans=NonActivePlansTable(
                rows=[
                    NonActivePlansRow(
                        id=f"{plan.id}",
                        plan_summary_url=self.url_index.get_plan_summary_url(plan.id),
                        prd_name=f"{plan.prd_name}",
                        description=plan.description.splitlines(),
                        price_per_unit=self.__format_price(plan.price_per_unit),
                        type_of_plan=self.__get_type_of_plan(plan.is_public_service),
                        plan_creation_date=self.__format_date(plan.plan_creation_date),
                    )
                    for plan in response.non_active_plans
                ],
            ),
            show_active_plans=bool(response.active_plans),
            active_plans=ActivePlansTable(
                rows=[
                    ActivePlansRow(
                        id=f"{plan.id}",
                        plan_summary_url=self.url_index.get_plan_summary_url(plan.id),
                        prd_name=f"{plan.prd_name}",
                        description=plan.description.splitlines(),
                        price_per_unit=self.__format_price(plan.price_per_unit),
                        type_of_plan=self.__get_type_of_plan(plan.is_public_service),
                        activation_date=self.__format_date(plan.activation_date),
                        expiration_date=self.__format_date(plan.expiration_date),
                        expiration_relative=f"{plan.expiration_relative} Tagen"
                        if plan.expiration_relative is not None
                        else "–",
                        is_available=plan.is_available,
                    )
                    for plan in response.active_plans
                ],
            ),
            show_expired_plans=bool(response.expired_plans),
            expired_plans=ExpiredPlansTable(
                rows=[
                    ExpiredPlansRow(
                        id=f"{plan.id}",
                        plan_summary_url=self.url_index.get_plan_summary_url(plan.id),
                        prd_name=f"{plan.prd_name}",
                        description=plan.description.splitlines(),
                        price_per_unit=self.__format_price(plan.price_per_unit),
                        type_of_plan=self.__get_type_of_plan(plan.is_public_service),
                        plan_creation_date=self.__format_date(plan.plan_creation_date),
                        renewed=plan.renewed,
                    )
                    for plan in response.expired_plans
                ],
            ),
        )

    def __get_type_of_plan(self, is_public_service: bool) -> str:
        return "Öffentlich" if is_public_service else "Produktiv"

    def __format_date(self, date: Optional[datetime]) -> str:
        return f"{date.strftime('%d.%m.%y')}" if date else "–"

    def __format_price(self, price_per_unit: Decimal) -> str:
        return f"{round(price_per_unit, 2)}"
