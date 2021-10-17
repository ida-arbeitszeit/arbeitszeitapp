from dataclasses import replace
from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.get_plan_summary import PlanSummarySuccess
from arbeitszeit_web.get_plan_summary import GetPlanSummarySuccessPresenter

TESTING_RESPONSE_MODEL = PlanSummarySuccess(
    plan_id=uuid4(),
    is_active=True,
    planner_id=uuid4(),
    product_name="test product name",
    description="test description",
    timeframe=7,
    production_unit="Piece",
    amount=100,
    means_cost=Decimal(1),
    resources_cost=Decimal(2),
    labour_cost=Decimal(3),
    is_public_service=False,
    price_per_unit=Decimal(0.06),
)


class GetPlanSummarySuccessPresenterTests(TestCase):
    def setUp(self) -> None:
        self.presenter = GetPlanSummarySuccessPresenter()

    def test_plan_id_is_displayed_correctly_as_tuple_of_strings(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertTupleEqual(
            view_model.plan_id, ("Plan-ID", str(TESTING_RESPONSE_MODEL.plan_id))
        )

    def test_active_status_is_displayed_correctly_as_tuple_of_strings(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertTupleEqual(view_model.is_active, ("Status", "Aktiv"))

    def test_inactive_status_is_displayed_correctly_as_tuple_of_strings(self):
        response = replace(
            TESTING_RESPONSE_MODEL,
            is_active=False,
        )
        view_model = self.presenter.present(response)
        self.assertTupleEqual(view_model.is_active, ("Status", "Inaktiv"))

    def test_planner_id_is_displayed_correctly_as_tuple_of_strings(self):
        expected_planner_id = uuid4()
        response = replace(
            TESTING_RESPONSE_MODEL,
            planner_id=expected_planner_id,
        )
        view_model = self.presenter.present(response)
        self.assertTupleEqual(
            view_model.planner_id, ("Planender Betrieb", str(expected_planner_id))
        )

    def test_product_name_is_displayed_correctly_as_tuple_of_strings(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertTupleEqual(
            view_model.product_name,
            ("Name des Produkts", TESTING_RESPONSE_MODEL.product_name),
        )

    def test_description_is_displayed_correctly_as_tuple_of_strings(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertTupleEqual(
            view_model.description,
            ("Beschreibung des Produkts", TESTING_RESPONSE_MODEL.description),
        )

    def test_description_is_displayed_correctly_as_tuple_of_strings_with_replaced_chars(
        self,
    ):
        response = replace(
            TESTING_RESPONSE_MODEL,
            description="test < test > test &",
        )
        view_model = self.presenter.present(response)
        self.assertTupleEqual(
            view_model.description,
            ("Beschreibung des Produkts", "test &lt; test &gt; test &amp;"),
        )

    def test_timeframe_is_displayed_correctly_as_tuple_of_strings(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertTupleEqual(
            view_model.timeframe,
            ("Planungszeitraum (Tage)", str(TESTING_RESPONSE_MODEL.timeframe)),
        )

    def test_production_unit_is_displayed_correctly_as_tuple_of_strings(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertTupleEqual(
            view_model.production_unit,
            ("Kleinste Abgabeeinheit", TESTING_RESPONSE_MODEL.production_unit),
        )

    def test_amount_is_displayed_correctly_as_tuple_of_strings(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertTupleEqual(
            view_model.amount,
            ("Menge", str(TESTING_RESPONSE_MODEL.amount)),
        )

    def test_means_cost_is_displayed_correctly_as_tuple_of_strings(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertTupleEqual(
            view_model.means_cost,
            ("Kosten für Produktionsmittel", str(TESTING_RESPONSE_MODEL.means_cost)),
        )

    def test_resources_cost_is_displayed_correctly_as_tuple_of_strings(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertTupleEqual(
            view_model.resources_cost,
            (
                "Kosten für Roh- und Hilfststoffe",
                str(TESTING_RESPONSE_MODEL.resources_cost),
            ),
        )

    def test_labour_cost_is_displayed_correctly_as_tuple_of_strings(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertTupleEqual(
            view_model.labour_cost,
            (
                "Arbeitsstunden",
                str(TESTING_RESPONSE_MODEL.labour_cost),
            ),
        )

    def test_type_of_plan_is_displayed_correctly_as_tuple_of_strings_when_productive_plan(
        self,
    ):
        response = replace(
            TESTING_RESPONSE_MODEL,
            is_public_service=False,
        )
        view_model = self.presenter.present(response)
        self.assertTupleEqual(
            view_model.type_of_plan,
            (
                "Art des Plans",
                "Produktiv",
            ),
        )

    def test_type_of_plan_is_displayed_correctly_as_tuple_of_strings_when_public_plan(
        self,
    ):
        response = replace(
            TESTING_RESPONSE_MODEL,
            is_public_service=True,
        )
        view_model = self.presenter.present(response)
        self.assertTupleEqual(
            view_model.type_of_plan,
            (
                "Art des Plans",
                "Öffentlich",
            ),
        )

    def test_price_per_unit_is_displayed_correctly_as_tuple_of_strings(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        self.assertTupleEqual(
            view_model.price_per_unit,
            (
                "Preis (pro Einheit)",
                str(TESTING_RESPONSE_MODEL.price_per_unit),
            ),
        )

    def test_that_to_dict_method_returns_a_dictionary(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        dictionary = view_model.to_dict()
        self.assertIsInstance(dictionary, dict)

    def test_that_to_dict_method_returns_a_dictionary_with_plan_id_tuple(self):
        view_model = self.presenter.present(TESTING_RESPONSE_MODEL)
        dictionary = view_model.to_dict()
        self.assertEqual(
            dictionary["plan_id"], ("Plan-ID", str(TESTING_RESPONSE_MODEL.plan_id))
        )
