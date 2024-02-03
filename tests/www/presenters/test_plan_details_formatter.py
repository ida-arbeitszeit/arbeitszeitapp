from decimal import Decimal
from uuid import uuid4

from arbeitszeit_web.formatters.plan_details_formatter import PlanDetailsFormatter
from tests.www.base_test_case import BaseTestCase
from tests.www.presenters.data_generators import PlanDetailsGenerator


class PlanDetailsFormatterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.formatter = self.injector.get(PlanDetailsFormatter)
        self.plan_details_generator = self.injector.get(PlanDetailsGenerator)
        self.plan_details = self.plan_details_generator.create_plan_details()
        self.session.login_company(company=uuid4())

    def test_plan_id_is_displayed_correctly_as_tuple_of_strings(self):
        web_details = self.formatter.format_plan_details(self.plan_details)
        self.assertTupleEqual(
            web_details.plan_id,
            (self.translator.gettext("Plan ID"), str(self.plan_details.plan_id)),
        )

    def test_active_status_is_displayed_correctly_as_tuple_of_strings(self):
        web_details = self.formatter.format_plan_details(self.plan_details)
        self.assertTupleEqual(
            web_details.activity_string,
            (self.translator.gettext("Status"), self.translator.gettext("Active")),
        )

    def test_inactive_status_is_displayed_correctly_as_tuple_of_strings(self):
        plan_details = self.plan_details_generator.create_plan_details(is_active=False)
        web_details = self.formatter.format_plan_details(plan_details)
        self.assertTupleEqual(
            web_details.activity_string,
            (self.translator.gettext("Status"), self.translator.gettext("Inactive")),
        )

    def test_planner_is_displayed_correctly_as_tuple_of_strings(self):
        PLANNER_ID = uuid4()
        PLANNER_NAME = "pl name"
        plan_details = self.plan_details_generator.create_plan_details(
            planner_id=PLANNER_ID, planner_name=PLANNER_NAME
        )
        web_details = self.formatter.format_plan_details(plan_details)
        self.assertTupleEqual(
            web_details.planner,
            (
                self.translator.gettext("Planning company"),
                str(PLANNER_ID),
                self.url_index.get_company_summary_url(company_id=PLANNER_ID),
                PLANNER_NAME,
            ),
        )

    def test_product_name_is_displayed_correctly_as_tuple_of_strings(self):
        PRODUCT_NAME = "pr name"
        plan_details = self.plan_details_generator.create_plan_details(
            product_name=PRODUCT_NAME
        )
        web_details = self.formatter.format_plan_details(plan_details)
        self.assertTupleEqual(
            web_details.product_name,
            (
                self.translator.gettext("Name of product"),
                PRODUCT_NAME,
            ),
        )

    def test_description_is_displayed_correctly_as_tuple_of_string_and_list_of_string(
        self,
    ):
        DESCRIPTION = "descr"
        plan_details = self.plan_details_generator.create_plan_details(
            description=DESCRIPTION
        )
        web_details = self.formatter.format_plan_details(plan_details)
        self.assertTupleEqual(
            web_details.description,
            (
                self.translator.gettext("Description of product"),
                [DESCRIPTION],
            ),
        )

    def test_description_is_splitted_correctly_at_carriage_return_in_list_of_strings(
        self,
    ):
        DESCRIPTION = "first paragraph\rsecond paragraph"
        plan_details = self.plan_details_generator.create_plan_details(
            description=DESCRIPTION
        )
        web_details = self.formatter.format_plan_details(plan_details)
        self.assertTupleEqual(
            web_details.description,
            (
                self.translator.gettext("Description of product"),
                ["first paragraph", "second paragraph"],
            ),
        )

    def test_timeframe_is_displayed_correctly_as_tuple_of_strings(self):
        web_details = self.formatter.format_plan_details(self.plan_details)
        self.assertTupleEqual(
            web_details.timeframe,
            (
                self.translator.gettext("Planning timeframe (days)"),
                str(self.plan_details.timeframe),
            ),
        )

    def test_production_unit_is_displayed_correctly_as_tuple_of_strings(self):
        web_details = self.formatter.format_plan_details(self.plan_details)
        self.assertTupleEqual(
            web_details.production_unit,
            (
                self.translator.gettext("Smallest delivery unit"),
                self.plan_details.production_unit,
            ),
        )

    def test_amount_is_displayed_correctly_as_tuple_of_strings(self):
        web_details = self.formatter.format_plan_details(self.plan_details)
        self.assertTupleEqual(
            web_details.amount,
            (self.translator.gettext("Amount"), str(self.plan_details.amount)),
        )

    def test_means_cost_is_displayed_correctly_as_tuple_of_strings(self):
        web_details = self.formatter.format_plan_details(self.plan_details)
        self.assertTupleEqual(
            web_details.means_cost,
            (
                self.translator.gettext("Costs for fixed means of production"),
                str(self.plan_details.means_cost),
            ),
        )

    def test_resources_cost_is_displayed_correctly_as_tuple_of_strings(self):
        web_details = self.formatter.format_plan_details(self.plan_details)
        self.assertTupleEqual(
            web_details.resources_cost,
            (
                self.translator.gettext("Costs for liquid means of production"),
                str(self.plan_details.resources_cost),
            ),
        )

    def test_labour_cost_is_displayed_correctly_as_tuple_of_strings(self):
        web_details = self.formatter.format_plan_details(self.plan_details)
        self.assertTupleEqual(
            web_details.labour_cost,
            (
                self.translator.gettext("Costs for work"),
                str(self.plan_details.labour_cost),
            ),
        )

    def test_type_of_plan_is_displayed_correctly_as_tuple_of_strings_when_productive_plan(
        self,
    ):
        plan_details = self.plan_details_generator.create_plan_details(
            is_public_service=False
        )
        web_details = self.formatter.format_plan_details(plan_details)
        self.assertTupleEqual(
            web_details.type_of_plan,
            (
                self.translator.gettext("Type"),
                self.translator.gettext("Productive"),
            ),
        )

    def test_type_of_plan_is_displayed_correctly_as_tuple_of_strings_when_public_plan(
        self,
    ):
        plan_details = self.plan_details_generator.create_plan_details(
            is_public_service=True
        )
        web_details = self.formatter.format_plan_details(plan_details)
        self.assertTupleEqual(
            web_details.type_of_plan,
            (
                self.translator.gettext("Type"),
                self.translator.gettext("Public"),
            ),
        )

    def test_price_per_unit_is_displayed_correctly_as_tuple_of_strings_and_bool(self):
        COOP_ID = uuid4()
        plan_details = self.plan_details_generator.create_plan_details(
            cooperation=COOP_ID, is_cooperating=True, price_per_unit=Decimal("0.061")
        )
        web_details = self.formatter.format_plan_details(plan_details)
        self.assertTupleEqual(
            web_details.price_per_unit,
            (
                self.translator.gettext("Price (per unit)"),
                "0.06",
                True,
                self.url_index.get_coop_summary_url(coop_id=COOP_ID),
            ),
        )

    def test_active_days_is_displayed_correctly_as_string(self):
        web_details = self.formatter.format_plan_details(self.plan_details)
        self.assertEqual(
            web_details.active_days,
            str(self.plan_details.active_days),
        )

    def test_correct_creation_date_is_shown(self):
        CREATION_DATE = self.datetime_service.now()
        plan_details = self.plan_details_generator.create_plan_details(
            creation_date=CREATION_DATE
        )
        web_details = self.formatter.format_plan_details(plan_details)
        self.assertEqual(
            web_details.creation_date,
            self.datetime_service.format_datetime(
                date=CREATION_DATE, zone="Europe/Berlin", fmt="%d.%m.%Y %H:%M"
            ),
        )

    def test_dash_is_shown_if_approval_date_does_not_exist(self):
        plan_details = self.plan_details_generator.create_plan_details(
            approval_date=None
        )
        web_details = self.formatter.format_plan_details(plan_details)
        self.assertEqual(web_details.approval_date, "-")

    def test_correct_approval_date_is_shown_if_it_exists(self):
        APPROVAL_DATE = self.datetime_service.now()
        plan_details = self.plan_details_generator.create_plan_details(
            approval_date=APPROVAL_DATE
        )
        web_details = self.formatter.format_plan_details(plan_details)
        self.assertEqual(
            web_details.approval_date,
            self.datetime_service.format_datetime(
                date=APPROVAL_DATE, zone="Europe/Berlin", fmt="%d.%m.%Y %H:%M"
            ),
        )

    def test_dash_is_shown_if_expiration_date_does_not_exist(self):
        plan_details = self.plan_details_generator.create_plan_details(
            expiration_date=None
        )
        web_details = self.formatter.format_plan_details(plan_details)
        self.assertEqual(web_details.expiration_date, "-")

    def test_correct_expiration_date_is_shown_if_it_exists(self):
        EXPIRATION_DATE = self.datetime_service.now()
        plan_details = self.plan_details_generator.create_plan_details(
            expiration_date=EXPIRATION_DATE
        )
        web_details = self.formatter.format_plan_details(plan_details)
        self.assertEqual(
            web_details.expiration_date,
            self.datetime_service.format_datetime(
                date=EXPIRATION_DATE,
                zone="Europe/Berlin",
                fmt="%d.%m.%Y %H:%M",
            ),
        )
