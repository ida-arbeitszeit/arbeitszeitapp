from datetime import datetime
from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.get_company_summary import (
    AccountBalances,
    GetCompanySummarySuccess,
    PlanDetails,
)
from arbeitszeit_web.get_company_summary import GetCompanySummarySuccessPresenter

from .dependency_injection import get_dependency_injector
from .url_index import PlanSummaryUrlIndexTestImpl

RESPONSE_WITH_2_PLANS = GetCompanySummarySuccess(
    id=uuid4(),
    name="Company Name",
    email="comp_mail@cp.org",
    registered_on=datetime(2022, 1, 2),
    account_balances=AccountBalances(
        Decimal("1"), Decimal("2"), Decimal("3"), Decimal("4.561")
    ),
    active_plans=[PlanDetails(uuid4(), "name_1"), PlanDetails(uuid4(), "name_2")],
)


class GetGetCompanySummaryPresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.presenter = self.injector.get(GetCompanySummarySuccessPresenter)
        self.plan_index = self.injector.get(PlanSummaryUrlIndexTestImpl)

    def test_company_id_is_shown(self):
        view_model = self.presenter.present(RESPONSE_WITH_2_PLANS)
        self.assertEqual(view_model.id, str(RESPONSE_WITH_2_PLANS.id))

    def test_company_name_is_shown(self):
        view_model = self.presenter.present(RESPONSE_WITH_2_PLANS)
        self.assertEqual(view_model.name, RESPONSE_WITH_2_PLANS.name)

    def test_company_email_is_shown(self):
        view_model = self.presenter.present(RESPONSE_WITH_2_PLANS)
        self.assertEqual(view_model.email, RESPONSE_WITH_2_PLANS.email)

    def test_company_register_date_is_shown(self):
        view_model = self.presenter.present(RESPONSE_WITH_2_PLANS)
        self.assertEqual(view_model.registered_on, RESPONSE_WITH_2_PLANS.registered_on)

    def test_company_account_balances_is_shown_as_list_of_strings(self):
        view_model = self.presenter.present(RESPONSE_WITH_2_PLANS)
        self.assertEqual(view_model.account_balances, ["1.00", "2.00", "3.00", "4.56"])

    def test_ids_of_plans_are_shown(self):
        view_model = self.presenter.present(RESPONSE_WITH_2_PLANS)
        self.assertEqual(
            view_model.active_plans[0].id,
            str(RESPONSE_WITH_2_PLANS.active_plans[0].id),
        )
        self.assertEqual(
            view_model.active_plans[1].id,
            str(RESPONSE_WITH_2_PLANS.active_plans[1].id),
        )

    def test_names_of_plans_are_shown(self):
        view_model = self.presenter.present(RESPONSE_WITH_2_PLANS)
        self.assertEqual(
            view_model.active_plans[0].name,
            str(RESPONSE_WITH_2_PLANS.active_plans[0].name),
        )
        self.assertEqual(
            view_model.active_plans[1].name,
            str(RESPONSE_WITH_2_PLANS.active_plans[1].name),
        )

    def test_urls_of_plans_are_shown(self):
        view_model = self.presenter.present(RESPONSE_WITH_2_PLANS)
        self.assertEqual(
            view_model.active_plans[0].url,
            self.plan_index.get_plan_summary_url(
                RESPONSE_WITH_2_PLANS.active_plans[0].id
            ),
        )
        self.assertEqual(
            view_model.active_plans[1].url,
            self.plan_index.get_plan_summary_url(
                RESPONSE_WITH_2_PLANS.active_plans[1].id
            ),
        )
