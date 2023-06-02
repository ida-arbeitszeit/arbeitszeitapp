from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from arbeitszeit_web.formatters.plan_summary_formatter import PlanSummaryFormatter
from arbeitszeit_web.session import UserRole
from tests.datetime_service import FakeDatetimeService
from tests.presenters.data_generators import PlanSummaryGenerator
from tests.session import FakeSession
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector
from .url_index import UrlIndexTestImpl


class PlanSummaryFormatterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.url_index = self.injector.get(UrlIndexTestImpl)
        self.translator = self.injector.get(FakeTranslator)
        self.formatter = self.injector.get(PlanSummaryFormatter)
        self.plan_summary_generator = self.injector.get(PlanSummaryGenerator)
        self.plan_summary = self.plan_summary_generator.create_plan_summary()
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.session = self.injector.get(FakeSession)
        self.session.login_company(company=uuid4())

    def test_plan_id_is_displayed_correctly_as_tuple_of_strings(self):
        web_summary = self.formatter.format_plan_summary(self.plan_summary)
        self.assertTupleEqual(
            web_summary.plan_id,
            (self.translator.gettext("Plan ID"), str(self.plan_summary.plan_id)),
        )

    def test_active_status_is_displayed_correctly_as_tuple_of_strings(self):
        web_summary = self.formatter.format_plan_summary(self.plan_summary)
        self.assertTupleEqual(
            web_summary.activity_string,
            (self.translator.gettext("Status"), self.translator.gettext("Active")),
        )

    def test_inactive_status_is_displayed_correctly_as_tuple_of_strings(self):
        plan_summary = self.plan_summary_generator.create_plan_summary(is_active=False)
        web_summary = self.formatter.format_plan_summary(plan_summary)
        self.assertTupleEqual(
            web_summary.activity_string,
            (self.translator.gettext("Status"), self.translator.gettext("Inactive")),
        )

    def test_planner_is_displayed_correctly_as_tuple_of_strings(self):
        PLANNER_ID = uuid4()
        PLANNER_NAME = "pl name"
        plan_summary = self.plan_summary_generator.create_plan_summary(
            planner_id=PLANNER_ID, planner_name=PLANNER_NAME
        )
        web_summary = self.formatter.format_plan_summary(plan_summary)
        self.assertTupleEqual(
            web_summary.planner,
            (
                self.translator.gettext("Planning company"),
                str(PLANNER_ID),
                self.url_index.get_company_summary_url(
                    user_role=UserRole.company, company_id=PLANNER_ID
                ),
                PLANNER_NAME,
            ),
        )

    def test_product_name_is_displayed_correctly_as_tuple_of_strings(self):
        PRODUCT_NAME = "pr name"
        plan_summary = self.plan_summary_generator.create_plan_summary(
            product_name=PRODUCT_NAME
        )
        web_summary = self.formatter.format_plan_summary(plan_summary)
        self.assertTupleEqual(
            web_summary.product_name,
            (
                self.translator.gettext("Name of product"),
                PRODUCT_NAME,
            ),
        )

    def test_description_is_displayed_correctly_as_tuple_of_string_and_list_of_string(
        self,
    ):
        DESCRIPTION = "descr"
        plan_summary = self.plan_summary_generator.create_plan_summary(
            description=DESCRIPTION
        )
        web_summary = self.formatter.format_plan_summary(plan_summary)
        self.assertTupleEqual(
            web_summary.description,
            (
                self.translator.gettext("Description of product"),
                [DESCRIPTION],
            ),
        )

    def test_description_is_splitted_correctly_at_carriage_return_in_list_of_strings(
        self,
    ):
        DESCRIPTION = "first paragraph\rsecond paragraph"
        plan_summary = self.plan_summary_generator.create_plan_summary(
            description=DESCRIPTION
        )
        web_summary = self.formatter.format_plan_summary(plan_summary)
        self.assertTupleEqual(
            web_summary.description,
            (
                self.translator.gettext("Description of product"),
                ["first paragraph", "second paragraph"],
            ),
        )

    def test_timeframe_is_displayed_correctly_as_tuple_of_strings(self):
        web_summary = self.formatter.format_plan_summary(self.plan_summary)
        self.assertTupleEqual(
            web_summary.timeframe,
            (
                self.translator.gettext("Planning timeframe (days)"),
                str(self.plan_summary.timeframe),
            ),
        )

    def test_production_unit_is_displayed_correctly_as_tuple_of_strings(self):
        web_summary = self.formatter.format_plan_summary(self.plan_summary)
        self.assertTupleEqual(
            web_summary.production_unit,
            (
                self.translator.gettext("Smallest delivery unit"),
                self.plan_summary.production_unit,
            ),
        )

    def test_amount_is_displayed_correctly_as_tuple_of_strings(self):
        web_summary = self.formatter.format_plan_summary(self.plan_summary)
        self.assertTupleEqual(
            web_summary.amount,
            (self.translator.gettext("Amount"), str(self.plan_summary.amount)),
        )

    def test_means_cost_is_displayed_correctly_as_tuple_of_strings(self):
        web_summary = self.formatter.format_plan_summary(self.plan_summary)
        self.assertTupleEqual(
            web_summary.means_cost,
            (
                self.translator.gettext("Costs for fixed means of production"),
                str(self.plan_summary.means_cost),
            ),
        )

    def test_resources_cost_is_displayed_correctly_as_tuple_of_strings(self):
        web_summary = self.formatter.format_plan_summary(self.plan_summary)
        self.assertTupleEqual(
            web_summary.resources_cost,
            (
                self.translator.gettext("Costs for liquid means of production"),
                str(self.plan_summary.resources_cost),
            ),
        )

    def test_labour_cost_is_displayed_correctly_as_tuple_of_strings(self):
        web_summary = self.formatter.format_plan_summary(self.plan_summary)
        self.assertTupleEqual(
            web_summary.labour_cost,
            (
                self.translator.gettext("Costs for work"),
                str(self.plan_summary.labour_cost),
            ),
        )

    def test_type_of_plan_is_displayed_correctly_as_tuple_of_strings_when_productive_plan(
        self,
    ):
        plan_summary = self.plan_summary_generator.create_plan_summary(
            is_public_service=False
        )
        web_summary = self.formatter.format_plan_summary(plan_summary)
        self.assertTupleEqual(
            web_summary.type_of_plan,
            (
                self.translator.gettext("Type"),
                self.translator.gettext("Productive"),
            ),
        )

    def test_type_of_plan_is_displayed_correctly_as_tuple_of_strings_when_public_plan(
        self,
    ):
        plan_summary = self.plan_summary_generator.create_plan_summary(
            is_public_service=True
        )
        web_summary = self.formatter.format_plan_summary(plan_summary)
        self.assertTupleEqual(
            web_summary.type_of_plan,
            (
                self.translator.gettext("Type"),
                self.translator.gettext("Public"),
            ),
        )

    def test_price_per_unit_is_displayed_correctly_as_tuple_of_strings_and_bool(self):
        COOP_ID = uuid4()
        plan_summary = self.plan_summary_generator.create_plan_summary(
            cooperation=COOP_ID, is_cooperating=True, price_per_unit=Decimal("0.061")
        )
        web_summary = self.formatter.format_plan_summary(plan_summary)
        self.assertTupleEqual(
            web_summary.price_per_unit,
            (
                self.translator.gettext("Price (per unit)"),
                "0.06",
                True,
                self.url_index.get_coop_summary_url(
                    user_role=UserRole.company, coop_id=COOP_ID
                ),
            ),
        )

    def test_availability_is_displayed_correctly_as_tuple_of_strings(self):
        plan_summary = self.plan_summary_generator.create_plan_summary(
            is_available=True
        )
        web_summary = self.formatter.format_plan_summary(plan_summary)
        self.assertTupleEqual(
            web_summary.availability_string,
            (
                self.translator.gettext("Product currently available"),
                self.translator.gettext("Yes"),
            ),
        )

    def test_active_days_is_displayed_correctly_as_string(self):
        web_summary = self.formatter.format_plan_summary(self.plan_summary)
        self.assertEqual(
            web_summary.active_days,
            str(self.plan_summary.active_days),
        )

    def test_correct_creation_date_is_shown(self):
        CREATION_DATE = self.datetime_service.now()
        plan_summary = self.plan_summary_generator.create_plan_summary(
            creation_date=CREATION_DATE
        )
        web_summary = self.formatter.format_plan_summary(plan_summary)
        self.assertEqual(
            web_summary.creation_date,
            self.datetime_service.format_datetime(
                date=CREATION_DATE, zone="Europe/Berlin", fmt="%d.%m.%Y %H:%M"
            ),
        )

    def test_dash_is_shown_if_approval_date_does_not_exist(self):
        plan_summary = self.plan_summary_generator.create_plan_summary(
            approval_date=None
        )
        web_summary = self.formatter.format_plan_summary(plan_summary)
        self.assertEqual(web_summary.approval_date, "-")

    def test_correct_approval_date_is_shown_if_it_exists(self):
        APPROVAL_DATE = self.datetime_service.now()
        plan_summary = self.plan_summary_generator.create_plan_summary(
            approval_date=APPROVAL_DATE
        )
        web_summary = self.formatter.format_plan_summary(plan_summary)
        self.assertEqual(
            web_summary.approval_date,
            self.datetime_service.format_datetime(
                date=APPROVAL_DATE, zone="Europe/Berlin", fmt="%d.%m.%Y %H:%M"
            ),
        )

    def test_dash_is_shown_if_expiration_date_does_not_exist(self):
        plan_summary = self.plan_summary_generator.create_plan_summary(
            expiration_date=None
        )
        web_summary = self.formatter.format_plan_summary(plan_summary)
        self.assertEqual(web_summary.expiration_date, "-")

    def test_correct_expiration_date_is_shown_if_it_exists(self):
        EXPIRATION_DATE = self.datetime_service.now()
        plan_summary = self.plan_summary_generator.create_plan_summary(
            expiration_date=EXPIRATION_DATE
        )
        web_summary = self.formatter.format_plan_summary(plan_summary)
        self.assertEqual(
            web_summary.expiration_date,
            self.datetime_service.format_datetime(
                date=EXPIRATION_DATE,
                zone="Europe/Berlin",
                fmt="%d.%m.%Y %H:%M",
            ),
        )
