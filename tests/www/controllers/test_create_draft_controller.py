from decimal import Decimal
from uuid import uuid4

from parameterized import parameterized

from arbeitszeit.use_cases import create_plan_draft
from arbeitszeit_web.forms import DraftForm
from arbeitszeit_web.www.controllers.create_draft_controller import (
    CreateDraftController,
)
from tests.request import FakeRequest
from tests.www.base_test_case import BaseTestCase

VALID_PRODUCT_NAME: str = "product name"
VALID_DESCRIPTION: str = "some description"
VALID_TIMEFRAME: str = "2"
VALID_PRD_UNIT: str = "1 piece"
VALID_PRD_AMOUNT: str = "10"
VALID_COSTS_P: str = "1.00"
VALID_COSTS_R: str = "2.00"
VALID_COSTS_A: str = "3.00"
VALID_IS_PUBLIC_PLAN: str = "on"


class CreateDraftControllerBase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(CreateDraftController)
        self.session.login_company(uuid4())

    def attach_form_data_to_request(
        self,
        request: FakeRequest,
        prd_name: str = VALID_PRODUCT_NAME,
        description: str = VALID_DESCRIPTION,
        timeframe: str = VALID_TIMEFRAME,
        prd_unit: str = VALID_PRD_UNIT,
        prd_amount: str = VALID_PRD_AMOUNT,
        costs_p: str = VALID_COSTS_P,
        costs_r: str = VALID_COSTS_R,
        costs_a: str = VALID_COSTS_A,
        is_public_plan: str = VALID_IS_PUBLIC_PLAN,
    ) -> FakeRequest:
        request.set_form("prd_name", prd_name)
        request.set_form("description", description)
        request.set_form("timeframe", timeframe)
        request.set_form("prd_unit", prd_unit)
        request.set_form("prd_amount", prd_amount)
        request.set_form("costs_p", costs_p)
        request.set_form("costs_r", costs_r)
        request.set_form("costs_a", costs_a)
        request.set_form("is_public_plan", is_public_plan)
        return request


class SuccessfulValidationTests(CreateDraftControllerBase):
    def test_that_correct_web_form_data_is_converted_to_use_case_request(self) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request)
        use_case_request = self.controller.import_form_data(request)
        assert isinstance(use_case_request, create_plan_draft.Request)

    def test_that_no_warning_is_displayed_if_form_data_is_valid(self) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request)
        self.controller.import_form_data(request)
        assert not self.notifier.warnings

    @parameterized.expand(
        [
            ("product name",),
            ("another product name",),
            ("  product name with whitespace  ",),
        ]
    )
    def test_that_use_case_request_contains_stripped_product_name_from_web_form(
        self, product_name: str
    ) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request, prd_name=product_name)
        use_case_request = self.controller.import_form_data(request)
        assert isinstance(use_case_request, create_plan_draft.Request)
        assert use_case_request.product_name == product_name.strip()

    @parameterized.expand(
        [
            ("some description",),
            ("another description\nwith newline",),
            [
                "  description with whitespace  ",
            ],
        ]
    )
    def test_that_use_case_request_contains_stripped_description_from_web_form(
        self, description: str
    ) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request, description=description)
        use_case_request = self.controller.import_form_data(request)
        assert isinstance(use_case_request, create_plan_draft.Request)
        assert use_case_request.description == description.strip()

    @parameterized.expand(
        [
            ("1",),
            ("5",),
            ("365",),
            ("  10  ",),
        ]
    )
    def test_that_use_case_request_contains_timeframe_from_web_form(
        self, timeframe: str
    ) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request, timeframe=timeframe)
        use_case_request = self.controller.import_form_data(request)
        assert isinstance(use_case_request, create_plan_draft.Request)
        assert use_case_request.timeframe_in_days == int(timeframe)

    @parameterized.expand(
        [
            ("1 piece",),
            ("1 kg",),
            ("  1 piece  ",),
        ]
    )
    def test_that_use_case_request_contains_stripped_production_unit_from_web_form(
        self, prd_unit: str
    ) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request, prd_unit=prd_unit)
        use_case_request = self.controller.import_form_data(request)
        assert isinstance(use_case_request, create_plan_draft.Request)
        assert use_case_request.production_unit == prd_unit.strip()

    @parameterized.expand(
        [
            ("10",),
            ("20",),
            ("  30  ",),
        ]
    )
    def test_that_use_case_request_contains_production_amount_from_web_form(
        self, prd_amount: str
    ) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request, prd_amount=prd_amount)
        use_case_request = self.controller.import_form_data(request)
        assert isinstance(use_case_request, create_plan_draft.Request)
        assert use_case_request.production_amount == int(prd_amount)

    @parameterized.expand(
        [
            ("0.00", "0", "2.00"),
            ("2.00", "3", "4"),
            ("  5.00  ", "6.00", "7.00"),
        ]
    )
    def test_that_use_case_request_contains_costs_from_web_form(
        self, costs_p: str, costs_r: str, costs_a: str
    ) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(
            request, costs_p=costs_p, costs_r=costs_r, costs_a=costs_a
        )
        use_case_request = self.controller.import_form_data(request)
        assert isinstance(use_case_request, create_plan_draft.Request)
        assert use_case_request.costs.labour_cost == Decimal(costs_a)
        assert use_case_request.costs.means_cost == Decimal(costs_p)
        assert use_case_request.costs.resource_cost == Decimal(costs_r)

    @parameterized.expand(
        [
            (
                "on",
                True,
            ),
            (
                "off",
                True,
            ),
            (
                " any text ",
                True,
            ),
            (
                "",
                False,
            ),
            (
                " ",
                False,
            ),
        ]
    )
    def test_that_use_case_request_contains_correct_public_plan_field_from_web_form(
        self, is_public_plan: str, expected: bool
    ) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(
            request, is_public_plan=is_public_plan
        )
        use_case_request = self.controller.import_form_data(request)
        assert isinstance(use_case_request, create_plan_draft.Request)
        assert use_case_request.is_public_service == expected


class UnsuccessfulValidationTests(CreateDraftControllerBase):
    def setUp(self):
        super().setUp()

    def test_that_invalid_form_data_is_converted_to_web_form(self) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request, prd_name="")
        web_form = self.controller.import_form_data(request)
        assert isinstance(web_form, DraftForm)

    def test_that_correct_warning_is_displayed_if_form_data_is_invalid(self) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request, prd_name="")
        self.controller.import_form_data(request)
        assert len(self.notifier.warnings) == 1
        assert self.notifier.warnings[0] == self.translator.gettext(
            "Please correct the errors in the form."
        )

    @parameterized.expand(
        [
            ("",),
            (" ",),
        ]
    )
    def test_that_product_name_is_required(self, product_name: str) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request, prd_name=product_name)
        web_form = self.controller.import_form_data(request)
        assert isinstance(web_form, DraftForm)
        assert web_form.product_name_errors == [
            self.translator.gettext("This field is required.")
        ]

    def test_that_product_name_must_be_at_most_100_characters_long(self) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request, prd_name="a" * 101)
        web_form = self.controller.import_form_data(request)
        assert isinstance(web_form, DraftForm)
        assert web_form.product_name_errors == [
            self.translator.gettext("This field must be at most 100 characters long.")
        ]

    @parameterized.expand(
        [
            ("",),
            (" ",),
        ]
    )
    def test_that_description_is_required(self, description: str) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request, description=description)
        web_form = self.controller.import_form_data(request)
        assert isinstance(web_form, DraftForm)
        assert web_form.description_errors == [
            self.translator.gettext("This field is required.")
        ]

    @parameterized.expand(
        [
            ("",),
            (" ",),
        ]
    )
    def test_that_timeframe_is_required(self, timeframe: str) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request, timeframe=timeframe)
        web_form = self.controller.import_form_data(request)
        assert isinstance(web_form, DraftForm)
        assert web_form.timeframe_errors == [
            self.translator.gettext("This field is required.")
        ]

    @parameterized.expand(
        [
            ("366", "This field must be an integer between 1 and 365."),
            ("0.9", "This field must be an integer."),
            ("0", "This field must be an integer between 1 and 365."),
            ("-1", "This field must be an integer between 1 and 365."),
            ("-1.5", "This field must be an integer."),
        ]
    )
    def test_that_timeframe_must_be_a_integer_from_1_to_365(
        self, timeframe: str, expected_error: str
    ) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request, timeframe=timeframe)
        web_form = self.controller.import_form_data(request)
        assert isinstance(web_form, DraftForm)
        assert web_form.timeframe_errors == [self.translator.gettext(expected_error)]

    @parameterized.expand(
        [
            ("",),
            (" ",),
        ]
    )
    def test_that_production_unit_is_required(self, production_unit: str) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request, prd_unit=production_unit)
        web_form = self.controller.import_form_data(request)
        assert isinstance(web_form, DraftForm)
        assert web_form.unit_of_distribution_errors == [
            self.translator.gettext("This field is required.")
        ]

    @parameterized.expand(
        [
            ("",),
            (" ",),
        ]
    )
    def test_that_production_amount_is_required(self, production_amount: str) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(
            request, prd_amount=production_amount
        )
        web_form = self.controller.import_form_data(request)
        assert isinstance(web_form, DraftForm)
        assert web_form.amount_errors == [
            self.translator.gettext("This field is required.")
        ]

    @parameterized.expand(
        [
            ("not an integer", "This field must be an integer."),
            ("1.5", "This field must be an integer."),
            ("-1.5", "This field must be an integer."),
            ("0", "This field must be an integer greater than or equal to 1."),
            ("-1", "This field must be an integer greater than or equal to 1."),
        ]
    )
    def test_that_production_amount_must_be_an_integer(
        self, production_amount: str, expected_error: str
    ) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(
            request, prd_amount=production_amount
        )
        web_form = self.controller.import_form_data(request)
        assert isinstance(web_form, DraftForm)
        assert web_form.amount_errors == [self.translator.gettext(expected_error)]

    @parameterized.expand(
        [
            ("",),
            (" ",),
        ]
    )
    def test_that_means_cost_is_required(self, means_cost: str) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request, costs_p=means_cost)
        web_form = self.controller.import_form_data(request)
        assert isinstance(web_form, DraftForm)
        assert web_form.means_cost_errors == [
            self.translator.gettext("This field is required.")
        ]

    @parameterized.expand(
        [
            ("not a decimal",),
            ("-0.1",),
            ("-2",),
        ]
    )
    def test_that_means_cost_must_be_a_positive_decimal_or_zero(
        self, means_cost: str
    ) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request, costs_p=means_cost)
        web_form = self.controller.import_form_data(request)
        assert isinstance(web_form, DraftForm)
        assert web_form.means_cost_errors == [
            self.translator.gettext("This field must be zero or a positive number.")
        ]

    @parameterized.expand(
        [
            ("",),
            (" ",),
        ]
    )
    def test_that_resource_cost_is_required(self, resource_cost: str) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request, costs_r=resource_cost)
        web_form = self.controller.import_form_data(request)
        assert isinstance(web_form, DraftForm)
        assert web_form.resource_cost_errors == [
            self.translator.gettext("This field is required.")
        ]

    @parameterized.expand(
        [
            ("not a decimal",),
            ("-0.1",),
            ("-2",),
        ]
    )
    def test_that_resource_cost_must_be_a_positive_decimal_or_zero(
        self, resource_cost: str
    ) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request, costs_r=resource_cost)
        web_form = self.controller.import_form_data(request)
        assert isinstance(web_form, DraftForm)
        assert web_form.resource_cost_errors == [
            self.translator.gettext("This field must be zero or a positive number.")
        ]

    @parameterized.expand(
        [
            ("",),
            (" ",),
        ]
    )
    def test_that_labour_cost_is_required(self, labour_cost: str) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request, costs_a=labour_cost)
        web_form = self.controller.import_form_data(request)
        assert isinstance(web_form, DraftForm)
        assert web_form.labour_cost_errors == [
            self.translator.gettext("This field is required.")
        ]

    @parameterized.expand(
        [
            ("not a decimal",),
            ("-0.1",),
            ("-2",),
        ]
    )
    def test_that_labour_cost_must_be_a_positive_decimal_or_zero(
        self, labour_cost: str
    ) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request, costs_a=labour_cost)
        web_form = self.controller.import_form_data(request)
        assert isinstance(web_form, DraftForm)
        assert web_form.labour_cost_errors == [
            self.translator.gettext("This field must be zero or a positive number.")
        ]

    @parameterized.expand(
        [
            ("0.00", "0.00", "0.00"),
            ("0", "0.0", "0.00"),
        ]
    )
    def test_that_error_is_displayed_if_all_cost_fields_are_zero_or_empty(
        self, costs_p: str, costs_r: str, costs_a: str
    ) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(
            request, costs_p=costs_p, costs_r=costs_r, costs_a=costs_a
        )
        web_form = self.controller.import_form_data(request)
        assert isinstance(web_form, DraftForm)
        assert web_form.general_errors == [
            self.translator.gettext(
                "At least one of the costs fields must be a positive number of hours."
            )
        ]
