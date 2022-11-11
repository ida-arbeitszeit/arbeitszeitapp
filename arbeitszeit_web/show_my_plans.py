from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.use_cases.show_my_plans import ShowMyPlansResponse
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import (
    HidePlanUrlIndex,
    RenewPlanUrlIndex,
    UrlIndex,
    UserUrlIndex,
)


@dataclass
class ActivePlansRow:
    plan_summary_url: str
    prd_name: str
    price_per_unit: str
    activation_date: str
    expiration_date: str
    expiration_relative: str
    is_available: bool
    is_cooperating: bool
    is_public_service: bool


@dataclass
class ActivePlansTable:
    rows: List[ActivePlansRow]


@dataclass
class NonActivePlansRow:
    plan_summary_url: str
    prd_name: str
    price_per_unit: str
    type_of_plan: str
    plan_creation_date: str


@dataclass
class NonActivePlansTable:
    rows: List[NonActivePlansRow]


@dataclass
class ExpiredPlansRow:
    plan_summary_url: str
    prd_name: str
    plan_creation_date: str
    renew_plan_url: str
    hide_plan_url: str
    is_public_service: bool


@dataclass
class ExpiredPlansTable:
    rows: List[ExpiredPlansRow]


@dataclass
class DraftsTableRow:
    product_name: str
    draft_creation_date: str
    draft_details_url: str
    draft_delete_url: str
    file_plan_url: str
    edit_plan_url: str


@dataclass
class DraftsTable:
    rows: List[DraftsTableRow]


@dataclass
class ShowMyPlansViewModel:
    show_non_active_plans: bool
    non_active_plans: NonActivePlansTable
    show_active_plans: bool
    active_plans: ActivePlansTable
    show_expired_plans: bool
    expired_plans: ExpiredPlansTable
    show_drafts: bool
    drafts: DraftsTable

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@inject
@dataclass
class ShowMyPlansPresenter:
    url_index: UrlIndex
    user_url_index: UserUrlIndex
    renew_plan_url_index: RenewPlanUrlIndex
    hide_plan_url_index: HidePlanUrlIndex
    translator: Translator
    datetime_service: DatetimeService
    notifier: Notifier

    def present(self, response: ShowMyPlansResponse) -> ShowMyPlansViewModel:
        if not response.count_all_plans:
            self.notifier.display_info(
                self.translator.gettext("You don't have any plans.")
            )
        return ShowMyPlansViewModel(
            show_active_plans=bool(response.active_plans),
            active_plans=self._create_active_plans_table(response),
            show_non_active_plans=bool(response.non_active_plans),
            non_active_plans=self._create_non_active_plans_table(response),
            show_expired_plans=bool(response.expired_plans),
            expired_plans=self._create_expired_plans_table(response),
            show_drafts=bool(response.drafts),
            drafts=self._create_drafts_table(response),
        )

    def _create_active_plans_table(
        self, response: ShowMyPlansResponse
    ) -> ActivePlansTable:
        return ActivePlansTable(
            rows=[
                ActivePlansRow(
                    plan_summary_url=self.user_url_index.get_plan_summary_url(plan.id),
                    prd_name=f"{plan.prd_name}",
                    price_per_unit=self.__format_price(plan.price_per_unit),
                    activation_date=self.__format_date(plan.activation_date),
                    expiration_date=self.__format_date(plan.expiration_date),
                    expiration_relative=self._format_days_until_expiration(
                        plan.expiration_date
                    ),
                    is_available=plan.is_available,
                    is_cooperating=plan.is_cooperating,
                    is_public_service=plan.is_public_service,
                )
                for plan in response.active_plans
            ],
        )

    def _create_non_active_plans_table(
        self, response: ShowMyPlansResponse
    ) -> NonActivePlansTable:
        return NonActivePlansTable(
            rows=[
                NonActivePlansRow(
                    plan_summary_url=self.user_url_index.get_plan_summary_url(plan.id),
                    prd_name=f"{plan.prd_name}",
                    price_per_unit=self.__format_price(plan.price_per_unit),
                    type_of_plan=self.__get_type_of_plan(plan.is_public_service),
                    plan_creation_date=self.__format_date(plan.plan_creation_date),
                )
                for plan in response.non_active_plans
            ],
        )

    def _create_expired_plans_table(
        self, response: ShowMyPlansResponse
    ) -> ExpiredPlansTable:
        return ExpiredPlansTable(
            rows=[
                ExpiredPlansRow(
                    plan_summary_url=self.user_url_index.get_plan_summary_url(plan.id),
                    prd_name=f"{plan.prd_name}",
                    is_public_service=plan.is_public_service,
                    plan_creation_date=self.__format_date(plan.plan_creation_date),
                    renew_plan_url=self.renew_plan_url_index.get_renew_plan_url(
                        plan.id
                    ),
                    hide_plan_url=self.hide_plan_url_index.get_hide_plan_url(plan.id),
                )
                for plan in response.expired_plans
            ],
        )

    def _create_drafts_table(self, response: ShowMyPlansResponse) -> DraftsTable:
        return DraftsTable(
            rows=[
                DraftsTableRow(
                    product_name=draft.prd_name,
                    draft_creation_date=self.__format_date(draft.plan_creation_date),
                    draft_details_url=self.url_index.get_draft_summary_url(draft.id),
                    draft_delete_url=self.url_index.get_delete_draft_url(draft.id),
                    file_plan_url=self.url_index.get_file_plan_url(draft.id),
                    edit_plan_url=self.url_index.get_draft_summary_url(draft.id),
                )
                for draft in response.drafts
            ]
        )

    def _format_days_until_expiration(
        self, expiration_datetime: Optional[datetime]
    ) -> str:
        if expiration_datetime is None:
            return "-"
        else:
            return str((expiration_datetime - self.datetime_service.now()).days)

    def __get_type_of_plan(self, is_public_service: bool) -> str:
        return (
            self.translator.gettext("Public")
            if is_public_service
            else self.translator.gettext("Productive")
        )

    def __format_date(self, date: Optional[datetime]) -> str:
        return date.strftime("%d.%m.%y") if date else "–"

    def __format_price(self, price_per_unit: Decimal) -> str:
        return f"{round(price_per_unit, 2)}"
