from dataclasses import replace
from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.plan_summary import BusinessPlanSummary
from arbeitszeit_web.plan_summary_service import PlanSummaryServiceImpl
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector
from .url_index import CompanySummaryUrlIndex, CoopSummaryUrlIndexTestImpl

BUSINESS_PLAN_SUMMARY = BusinessPlanSummary(
    plan_id=uuid4(),
    is_active=True,
    planner_id=uuid4(),
    planner_name="test planner name",
    product_name="test product name",
    description="test description",
    timeframe=7,
    production_unit="Piece",
    amount=100,
    means_cost=Decimal(1),
    resources_cost=Decimal(2),
    labour_cost=Decimal(3),
    is_public_service=False,
    price_per_unit=Decimal("0.061"),
    is_available=True,
    is_cooperating=True,
    cooperation=uuid4(),
)


class PlanSummaryServiceTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.coop_url_index = self.injector.get(CoopSummaryUrlIndexTestImpl)
        self.company_url_index = self.injector.get(CompanySummaryUrlIndex)
        self.translator = self.injector.get(FakeTranslator)
        self.service = self.injector.get(PlanSummaryServiceImpl)

    def test_plan_id_is_displayed_correctly_as_tuple_of_strings(self):
        plan_summary = self.service.get_plan_summary_member(BUSINESS_PLAN_SUMMARY)
        self.assertTupleEqual(
            plan_summary.plan_id, ("Plan-ID", str(BUSINESS_PLAN_SUMMARY.plan_id))
        )

    def test_active_status_is_displayed_correctly_as_tuple_of_strings(self):
        plan_summary = self.service.get_plan_summary_member(BUSINESS_PLAN_SUMMARY)
        self.assertTupleEqual(plan_summary.is_active, ("Status", "Aktiv"))

    def test_inactive_status_is_displayed_correctly_as_tuple_of_strings(self):
        response = replace(
            BUSINESS_PLAN_SUMMARY,
            is_active=False,
        )
        plan_summary = self.service.get_plan_summary_member(response)
        self.assertTupleEqual(plan_summary.is_active, ("Status", "Inaktiv"))

    def test_planner_is_displayed_correctly_as_tuple_of_strings(self):
        expected_planner_id = uuid4()
        response = replace(
            BUSINESS_PLAN_SUMMARY,
            planner_id=expected_planner_id,
        )
        plan_summary = self.service.get_plan_summary_member(response)
        self.assertTupleEqual(
            plan_summary.planner,
            (
                self.translator.gettext("Planning company"),
                str(expected_planner_id),
                self.company_url_index.get_company_summary_url(expected_planner_id),
                BUSINESS_PLAN_SUMMARY.planner_name,
            ),
        )

    def test_product_name_is_displayed_correctly_as_tuple_of_strings(self):
        plan_summary = self.service.get_plan_summary_member(BUSINESS_PLAN_SUMMARY)
        self.assertTupleEqual(
            plan_summary.product_name,
            (
                self.translator.gettext("Name of product"),
                BUSINESS_PLAN_SUMMARY.product_name,
            ),
        )

    def test_description_is_displayed_correctly_as_tuple_of_string_and_list_of_string(
        self,
    ):
        plan_summary = self.service.get_plan_summary_member(BUSINESS_PLAN_SUMMARY)
        self.assertTupleEqual(
            plan_summary.description,
            (
                self.translator.gettext("Description of product"),
                [BUSINESS_PLAN_SUMMARY.description],
            ),
        )

    def test_description_is_splitted_correctly_at_carriage_return_in_list_of_strings(
        self,
    ):
        response = replace(
            BUSINESS_PLAN_SUMMARY,
            description="first paragraph\rsecond paragraph",
        )
        plan_summary = self.service.get_plan_summary_member(response)
        self.assertTupleEqual(
            plan_summary.description,
            (
                self.translator.gettext("Description of product"),
                ["first paragraph", "second paragraph"],
            ),
        )

    def test_timeframe_is_displayed_correctly_as_tuple_of_strings(self):
        plan_summary = self.service.get_plan_summary_member(BUSINESS_PLAN_SUMMARY)
        self.assertTupleEqual(
            plan_summary.timeframe,
            ("Planungszeitraum (Tage)", str(BUSINESS_PLAN_SUMMARY.timeframe)),
        )

    def test_production_unit_is_displayed_correctly_as_tuple_of_strings(self):
        plan_summary = self.service.get_plan_summary_member(BUSINESS_PLAN_SUMMARY)
        self.assertTupleEqual(
            plan_summary.production_unit,
            ("Kleinste Abgabeeinheit", BUSINESS_PLAN_SUMMARY.production_unit),
        )

    def test_amount_is_displayed_correctly_as_tuple_of_strings(self):
        plan_summary = self.service.get_plan_summary_member(BUSINESS_PLAN_SUMMARY)
        self.assertTupleEqual(
            plan_summary.amount,
            ("Menge", str(BUSINESS_PLAN_SUMMARY.amount)),
        )

    def test_means_cost_is_displayed_correctly_as_tuple_of_strings(self):
        plan_summary = self.service.get_plan_summary_member(BUSINESS_PLAN_SUMMARY)
        self.assertTupleEqual(
            plan_summary.means_cost,
            ("Kosten für Produktionsmittel", str(BUSINESS_PLAN_SUMMARY.means_cost)),
        )

    def test_resources_cost_is_displayed_correctly_as_tuple_of_strings(self):
        plan_summary = self.service.get_plan_summary_member(BUSINESS_PLAN_SUMMARY)
        self.assertTupleEqual(
            plan_summary.resources_cost,
            (
                "Kosten für Roh- und Hilfststoffe",
                str(BUSINESS_PLAN_SUMMARY.resources_cost),
            ),
        )

    def test_labour_cost_is_displayed_correctly_as_tuple_of_strings(self):
        plan_summary = self.service.get_plan_summary_member(BUSINESS_PLAN_SUMMARY)
        self.assertTupleEqual(
            plan_summary.labour_cost,
            (
                "Arbeitsstunden",
                str(BUSINESS_PLAN_SUMMARY.labour_cost),
            ),
        )

    def test_type_of_plan_is_displayed_correctly_as_tuple_of_strings_when_productive_plan(
        self,
    ):
        response = replace(
            BUSINESS_PLAN_SUMMARY,
            is_public_service=False,
        )
        plan_summary = self.service.get_plan_summary_member(response)
        self.assertTupleEqual(
            plan_summary.type_of_plan,
            (
                "Art des Plans",
                "Produktiv",
            ),
        )

    def test_type_of_plan_is_displayed_correctly_as_tuple_of_strings_when_public_plan(
        self,
    ):
        response = replace(
            BUSINESS_PLAN_SUMMARY,
            is_public_service=True,
        )
        plan_summary = self.service.get_plan_summary_member(response)
        self.assertTupleEqual(
            plan_summary.type_of_plan,
            (
                "Art des Plans",
                "Öffentlich",
            ),
        )

    def test_price_per_unit_is_displayed_correctly_as_tuple_of_strings_and_bool(self):
        plan_summary = self.service.get_plan_summary_member(BUSINESS_PLAN_SUMMARY)
        coop_id = BUSINESS_PLAN_SUMMARY.cooperation
        assert coop_id
        self.assertTupleEqual(
            plan_summary.price_per_unit,
            (
                "Preis (pro Einheit)",
                "0.06",
                True,
                self.coop_url_index.get_coop_summary_url(coop_id),
            ),
        )

    def test_availability_is_displayed_correctly_as_tuple_of_strings(self):
        plan_summary = self.service.get_plan_summary_member(BUSINESS_PLAN_SUMMARY)
        self.assertTupleEqual(
            plan_summary.is_available,
            (
                "Produkt aktuell verfügbar",
                "Ja",
            ),
        )
