from dataclasses import replace
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from parameterized import parameterized

from arbeitszeit.interactors.get_coop_summary import (
    AssociatedPlan,
    GetCoopSummaryResponse,
)
from arbeitszeit_web.www.presenters.get_coop_summary_presenter import (
    GetCoopSummarySuccessPresenter,
)
from tests.www.base_test_case import BaseTestCase


class GetCoopSummarySuccessPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetCoopSummarySuccessPresenter)
        self.session.login_company(company=uuid4())

    def test_coop_id_is_displayed_correctly(self):
        coop_summary = self.get_coop_summary()
        view_model = self.presenter.present(coop_summary)
        self.assertEqual(view_model.coop_id, str(view_model.coop_id))

    def test_coop_name_is_displayed_correctly(self):
        coop_summary = self.get_coop_summary()
        view_model = self.presenter.present(coop_summary)
        self.assertEqual(view_model.coop_name, view_model.coop_name)

    @parameterized.expand(["coop def\ncoop def2", "coop def\n\rcoop def2"])
    def test_coop_definition_is_displayed_correctly_as_list_of_strings(
        self, coop_definition: str
    ):
        expected_definition = coop_definition.splitlines()
        coop_summary = self.get_coop_summary(coop_definition=coop_definition)
        view_model = self.presenter.present(coop_summary)
        self.assertEqual(view_model.coop_definition, expected_definition)

    def test_no_url_to_request_coordination_transfer_page_is_displayed_if_user_is_not_coordinator(
        self,
    ):
        coop_summary = self.get_coop_summary(requester_is_coordinator=False)
        view_model = self.presenter.present(coop_summary)
        self.assertIsNone(view_model.transfer_coordination_url)

    def test_url_to_request_coordination_transfer_page_is_displayed_if_user_is_coordinator(
        self,
    ):
        coop_summary = self.get_coop_summary(requester_is_coordinator=True)
        view_model = self.presenter.present(coop_summary)
        self.assertIsNotNone(view_model.transfer_coordination_url)

    def test_correct_url_to_request_coordination_transfer_page_is_displayed_if_user_is_coordinator(
        self,
    ):
        coop_summary = self.get_coop_summary(requester_is_coordinator=True)
        view_model = self.presenter.present(coop_summary)
        self.assertEqual(
            view_model.transfer_coordination_url,
            self.url_index.get_request_coordination_transfer_url(
                coop_id=coop_summary.coop_id,
            ),
        )

    def test_coordinator_id_is_displayed_correctly(self):
        coop_summary = self.get_coop_summary()
        view_model = self.presenter.present(coop_summary)
        self.assertEqual(
            view_model.current_coordinator_id,
            str(coop_summary.current_coordinator),
        )

    def test_coordinator_name_is_displayed_correctly(self):
        expected_coordinator_name = "A coordinator name"
        coop_summary = self.get_coop_summary(coordinator_name=expected_coordinator_name)
        view_model = self.presenter.present(coop_summary)
        self.assertEqual(
            view_model.current_coordinator_name,
            expected_coordinator_name,
        )

    def test_link_to_coordinators_company_summary_page_is_displayed_correctly(self):
        coop_summary = self.get_coop_summary()
        view_model = self.presenter.present(coop_summary)
        self.assertEqual(
            view_model.current_coordinator_url,
            self.url_index.get_company_summary_url(
                company_id=coop_summary.current_coordinator,
            ),
        )

    def test_link_to_list_of_coordinators_is_displayed_correctly(self):
        coop_summary = self.get_coop_summary()
        view_model = self.presenter.present(coop_summary)
        self.assertEqual(
            view_model.list_of_coordinators_url,
            self.url_index.get_list_of_coordinators_url(
                cooperation_id=coop_summary.coop_id,
            ),
        )

    def test_coop_price_is_displayed_correctly_if_it_is_not_none(self):
        coop_price = Decimal(50.005)
        expected_coop_price = f"{round(coop_price, 2)}"
        coop_summary = self.get_coop_summary(coop_price=coop_price)
        view_model = self.presenter.present(coop_summary)
        self.assertEqual(
            view_model.coop_price,
            expected_coop_price,
        )

    def test_coop_price_is_displayed_as_a_dash_if_coop_price_is_none(self):
        coop_summary = self.get_coop_summary()
        coop_summary = replace(coop_summary, coop_price=None)
        view_model = self.presenter.present(coop_summary)
        self.assertEqual(
            view_model.coop_price,
            "-",
        )

    def test_first_plans_name_is_displayed_correctly(self):
        coop_summary = self.get_coop_summary()
        view_model = self.presenter.present(coop_summary)
        self.assertEqual(view_model.plans[0].plan_name, coop_summary.plans[0].plan_name)

    @parameterized.expand([(Decimal("1"),), (Decimal("0"),), (Decimal("0.509"),)])
    def test_first_plans_individual_price_is_displayed_correctly(
        self, plan_individual_price: Decimal
    ):
        expected_price = f"{round(plan_individual_price, 2)}"
        coop_summary = self.get_coop_summary(
            plans=[
                self.get_associated_plan(plan_individual_price=plan_individual_price)
            ]
        )
        view_model = self.presenter.present(coop_summary)
        self.assertEqual(view_model.plans[0].plan_individual_price, expected_price)

    def test_first_plans_plan_id_is_displayed_correctly(self):
        coop_summary = self.get_coop_summary()
        view_model = self.presenter.present(coop_summary)
        assert view_model.plans[0].plan_id == str(coop_summary.plans[0].plan_id)

    def test_first_plans_planner_name_is_displayed_correctly(self):
        coop_summary = self.get_coop_summary()
        view_model = self.presenter.present(coop_summary)
        self.assertEqual(
            view_model.plans[0].planner_name,
            coop_summary.plans[0].planner_name,
        )

    def test_url_to_first_plans_planner_company_summary_page_is_displayed_correctly(
        self,
    ):
        coop_summary = self.get_coop_summary()
        view_model = self.presenter.present(coop_summary)
        self.assertEqual(
            view_model.plans[0].planner_url,
            self.url_index.get_company_summary_url(
                company_id=coop_summary.plans[0].planner_id,
            ),
        )

    def test_no_plans_are_shown_when_there_are_no_plans_associated(self) -> None:
        coop_summary = self.get_coop_summary(plans=[])
        view_model = self.presenter.present(coop_summary)
        assert not view_model.plans

    def test_two_plans_are_shown_when_there_are_two_plans_associated(self) -> None:
        coop_summary = self.get_coop_summary(
            plans=[self.get_associated_plan(), self.get_associated_plan()]
        )
        view_model = self.presenter.present(coop_summary)
        assert len(view_model.plans) == 2

    @parameterized.expand(
        [
            (True, True, True),
            (True, False, True),
            (False, True, True),
            (False, False, False),
        ]
    )
    def test_end_coop_button_of_plan_is_shown_only_when_requester_is_coordinator_or_planner(
        self,
        requester_is_coordinator: bool,
        requester_is_planner: bool,
        button_is_shown: bool,
    ) -> None:
        plan = self.get_associated_plan(requester_is_planner=requester_is_planner)
        coop_summary = self.get_coop_summary(
            requester_is_coordinator=requester_is_coordinator, plans=[plan]
        )
        view_model = self.presenter.present(response=coop_summary)
        assert view_model.plans[0].show_end_coop_button == button_is_shown

    def get_associated_plan(
        self,
        requester_is_planner: Optional[bool] = None,
        plan_individual_price: Optional[Decimal] = None,
    ) -> AssociatedPlan:
        if requester_is_planner is None:
            requester_is_planner = False
        if plan_individual_price is None:
            plan_individual_price = Decimal("1")
        return AssociatedPlan(
            plan_id=uuid4(),
            plan_name="plan_name",
            plan_individual_price=plan_individual_price,
            planner_id=uuid4(),
            planner_name="A Cooperating Company Coop.",
            requester_is_planner=requester_is_planner,
        )

    def get_coop_summary(
        self,
        plans: Optional[list[AssociatedPlan]] = None,
        requester_is_coordinator: Optional[bool] = None,
        coop_definition: Optional[str] = None,
        coordinator_name: Optional[str] = None,
        coop_price: Optional[Decimal] = None,
    ) -> GetCoopSummaryResponse:
        if plans is None:
            plans = [self.get_associated_plan()]
        if requester_is_coordinator is None:
            requester_is_coordinator = True
        if coop_definition is None:
            coop_definition = "coop def\ncoop def2"
        if coordinator_name is None:
            coordinator_name = "coordinator name"
        if coop_price is None:
            coop_price = Decimal(50.005)
        return GetCoopSummaryResponse(
            requester_is_coordinator=requester_is_coordinator,
            coop_id=uuid4(),
            coop_name="coop name",
            coop_definition=coop_definition,
            current_coordinator=uuid4(),
            current_coordinator_name=coordinator_name,
            coop_price=coop_price,
            plans=plans,
        )
