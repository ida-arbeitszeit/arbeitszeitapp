from datetime import datetime
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.get_company_summary import (
    GetCompanySummarySuccess,
    PlanDetails,
)
from arbeitszeit_web.get_company_summary import GetCompanySummarySuccessPresenter

RESPONSE_WITH_2_PLANS = GetCompanySummarySuccess(
    name="Company Name",
    email="comp_mail@cp.org",
    registered_on=datetime(2022, 1, 2),
    active_plans=[PlanDetails(uuid4(), "name_1"), PlanDetails(uuid4(), "name_2")],
)


class GetGetCompanySummaryPresenterTests(TestCase):
    def setUp(self) -> None:
        self.presenter = GetCompanySummarySuccessPresenter()

    def test_company_name_is_shown(self):
        view_model = self.presenter.present(RESPONSE_WITH_2_PLANS)
        self.assertEqual(view_model.name, RESPONSE_WITH_2_PLANS.name)

    def test_company_email_is_shown(self):
        view_model = self.presenter.present(RESPONSE_WITH_2_PLANS)
        self.assertEqual(view_model.email, RESPONSE_WITH_2_PLANS.email)

    def test_company_register_date_is_shown(self):
        view_model = self.presenter.present(RESPONSE_WITH_2_PLANS)
        self.assertEqual(view_model.registered_on, RESPONSE_WITH_2_PLANS.registered_on)

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
