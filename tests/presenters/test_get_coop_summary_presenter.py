from dataclasses import replace
from decimal import Decimal
from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.use_cases.get_coop_summary import AssociatedPlan, GetCoopSummarySuccess
from arbeitszeit_web.get_coop_summary import GetCoopSummarySuccessPresenter

TESTING_RESPONSE_MODEL = GetCoopSummarySuccess(
    requester_is_coordinator=True,
    coop_id=uuid4(),
    coop_name="coop name",
    coop_definition="coop def\ncoop def2",
    coordinator_id=uuid4(),
    plans=[
        AssociatedPlan(
            plan_id=uuid4(),
            plan_name="plan_name",
            plan_individual_price=Decimal("1"),
            plan_coop_price=Decimal(50.005),
        )
    ],
)


class GetCoopSummarySuccessPresenterTests(TestCase):
    def setUp(self) -> None:
        self.plan_url_index = PlanSummaryUrlIndex()
        self.presenter = GetCoopSummarySuccessPresenter(self.plan_url_index)

    def test_end_coop_button_is_shown_when_requester_is_coordinator(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertTrue(view_model.show_end_coop_button)

    def test_end_coop_button_is_not_shown_when_requester_not_coordinator(self):
        response = replace(
            TESTING_RESPONSE_MODEL,
            requester_is_coordinator=False,
        )
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.show_end_coop_button)

    def test_coop_id_is_displayed_correctly(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertEqual(view_model.coop_id, str(TESTING_RESPONSE_MODEL.coop_id))

    def test_coop_name_is_displayed_correctly(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertEqual(view_model.coop_name, TESTING_RESPONSE_MODEL.coop_name)

    def test_coop_definition_is_displayed_correctly_as_list_of_strings(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertEqual(view_model.coop_definition, ["coop def", "coop def2"])

    def test_coordinator_id_is_displayed_correctly(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertEqual(
            view_model.coordinator_id, str(TESTING_RESPONSE_MODEL.coordinator_id)
        )

    def test_first_plan_name_is_displayed_correctly(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertEqual(
            view_model.plans[0].plan_name, TESTING_RESPONSE_MODEL.plans[0].plan_name
        )

    def test_first_plan_individual_price_is_displayed_correctly(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertEqual(
            view_model.plans[0].plan_individual_price,
            "1.00",
        )

    def test_first_plan_coop_price_is_displayed_correctly(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertEqual(
            view_model.plans[0].plan_coop_price,
            "50.01",
        )


class PlanSummaryUrlIndex:
    def get_plan_summary_url(self, plan_id: UUID) -> str:
        return f"fake_plan_url:{plan_id}"
