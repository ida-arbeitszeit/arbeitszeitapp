from decimal import Decimal
from uuid import uuid4

from parameterized import parameterized

from arbeitszeit_web.www.controllers.edit_draft_controller import EditDraftController
from tests.forms import DraftForm
from tests.www.base_test_case import BaseTestCase


class EditDraftControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(EditDraftController)
        self.session.login_company(uuid4())

    @parameterized.expand(
        [
            "test name",
            "other test name",
        ]
    )
    def test_that_product_name_from_form_field_is_used_in_request(
        self, expected_name: str
    ) -> None:
        form = self.create_form(product_name=expected_name)
        request = self.controller.process_form(form=form, draft_id=uuid4())
        assert request
        assert request.product_name == expected_name

    def test_that_empty_product_name_field_produces_error_message_on_form_field(
        self,
    ) -> None:
        form = self.create_form(product_name="")
        self.controller.process_form(form=form, draft_id=uuid4())
        assert form.product_name_field().errors

    def test_that_empty_product_name_field_produces_the_correct_error_message(
        self,
    ) -> None:
        form = self.create_form(product_name="")
        self.controller.process_form(form=form, draft_id=uuid4())
        assert (
            self.translator.gettext("The product name field cannot be empty.")
            in form.product_name_field().errors
        )

    @parameterized.expand(
        [
            "test description",
            "other test description",
        ]
    )
    def test_that_description_from_field_is_used_in_request(
        self, expected_description: str
    ) -> None:
        form = self.create_form(description=expected_description)
        request = self.controller.process_form(form=form, draft_id=uuid4())
        assert request
        assert request.description == expected_description

    def test_that_empty_description_field_produces_an_error_message_on_the_description_field(
        self,
    ) -> None:
        form = self.create_form(description="")
        self.controller.process_form(form=form, draft_id=uuid4())
        assert form.description_field().errors

    def test_that_empty_description_field_attaches_correct_error_message_to_description_field(
        self,
    ) -> None:
        form = self.create_form(description="")
        self.controller.process_form(form=form, draft_id=uuid4())
        assert (
            self.translator.gettext("The description field cannot be empty.")
            in form.description_field().errors
        )

    @parameterized.expand(
        [
            "test unit",
            "other test unit",
        ]
    )
    def test_that_delivery_unit_from_field_is_used_in_request(
        self, expected_unit: str
    ) -> None:
        form = self.create_form(unit_of_distribution=expected_unit)
        request = self.controller.process_form(form=form, draft_id=uuid4())
        assert request
        assert request.unit_of_distribution == expected_unit

    @parameterized.expand(
        [
            "product_name",
            "description",
            "unit_of_distribution",
        ]
    )
    def test_that_empty_values_for_mandatory_string_fields_are_rejected(
        self, field_name: str
    ) -> None:
        form = self.create_form(**{field_name: ""})  # type: ignore
        request = self.controller.process_form(form=form, draft_id=uuid4())
        assert request is None

    def test_that_empty_unit_of_distritution_field_produces_an_error_on_that_field(
        self,
    ) -> None:
        form = self.create_form(unit_of_distribution="")
        self.controller.process_form(form=form, draft_id=uuid4())
        assert form.unit_of_distribution_field().errors

    def test_that_empty_unit_of_distribution_field_attaches_correct_error_message_to_that_field(
        self,
    ) -> None:
        form = self.create_form(unit_of_distribution="")
        self.controller.process_form(form=form, draft_id=uuid4())
        assert (
            self.translator.gettext("The smallest delivery unit field cannot be empty.")
            in form.unit_of_distribution_field().errors
        )

    def test_that_request_is_rejected_with_total_cost_zero(self) -> None:
        form = self.create_form(
            labour_cost=Decimal(0),
            resource_cost=Decimal(0),
            means_cost=Decimal(0),
        )
        request = self.controller.process_form(form=form, draft_id=uuid4())
        assert request is None

    def test_that_correct_warning_is_displayed_when_all_costs_are_zero(self) -> None:
        form = self.create_form(
            labour_cost=Decimal(0),
            resource_cost=Decimal(0),
            means_cost=Decimal(0),
        )
        self.controller.process_form(form=form, draft_id=uuid4())
        assert (
            self.translator.gettext(
                "At least one of the costs fields must be a positive number of hours."
            )
            in self.notifier.warnings
        )

    @parameterized.expand(
        [
            Decimal(1),
            Decimal(3),
            Decimal(123),
            Decimal(0),
        ]
    )
    def test_that_labour_cost_fields_from_form_are_used_in_request(
        self, costs: Decimal
    ) -> None:
        form = self.create_form(labour_cost=costs)
        request = self.controller.process_form(form=form, draft_id=uuid4())
        assert request
        assert request.labour_cost == costs

    @parameterized.expand(
        [
            Decimal(1),
            Decimal(2),
            Decimal(612),
            Decimal(0),
        ]
    )
    def test_that_means_cost_fields_from_form_are_used_in_request(
        self, costs: Decimal
    ) -> None:
        form = self.create_form(means_cost=costs)
        request = self.controller.process_form(form=form, draft_id=uuid4())
        assert request
        assert request.means_cost == costs

    @parameterized.expand(
        [
            Decimal(1),
            Decimal(6),
            Decimal(212),
            Decimal(0),
        ]
    )
    def test_that_resource_cost_fields_from_form_are_used_in_request(
        self, costs: Decimal
    ) -> None:
        form = self.create_form(resource_cost=costs)
        request = self.controller.process_form(form=form, draft_id=uuid4())
        assert request
        assert request.resource_cost == costs

    @parameterized.expand([0, -1])
    def test_that_invalid_amount_values_are_rejected(self, amount: int) -> None:
        form = self.create_form(amount=amount)
        request = self.controller.process_form(form=form, draft_id=uuid4())
        assert request is None

    @parameterized.expand([1, 12, 75452])
    def test_that_the_amount_field_is_used_in_the_request(self, amount: int) -> None:
        form = self.create_form(amount=amount)
        request = self.controller.process_form(form=form, draft_id=uuid4())
        assert request
        assert request.amount == amount

    @parameterized.expand(
        [
            (
                0,
                "The product amount planned cannot be 0.",
            ),
            (
                -1,
                "The planned product amount cannot be negative.",
            ),
        ]
    )
    def test_that_invalid_amount_values_produce_correct_error_message_on_that_field(
        self, amount: int, expected_message: str
    ) -> None:
        form = self.create_form(amount=amount)
        self.controller.process_form(form=form, draft_id=uuid4())
        assert self.translator.gettext(expected_message) in form.amount_field().errors

    @parameterized.expand([True, False])
    def test_that_the_is_public_service_field_is_used_in_request(
        self, expected_is_public_service: bool
    ) -> None:
        form = self.create_form(is_public_service=expected_is_public_service)
        request = self.controller.process_form(form=form, draft_id=uuid4())
        assert request
        assert request.is_public_service == expected_is_public_service

    @parameterized.expand([0, -1])
    def test_that_invalid_timeframe_values_are_rejected(self, timeframe: int) -> None:
        form = self.create_form(timeframe=timeframe)
        request = self.controller.process_form(form=form, draft_id=uuid4())
        assert request is None

    @parameterized.expand([1, 12, 75452])
    def test_that_the_timeframe_field_is_used_in_the_request(
        self, timeframe: int
    ) -> None:
        form = self.create_form(timeframe=timeframe)
        request = self.controller.process_form(form=form, draft_id=uuid4())
        assert request
        assert request.timeframe == timeframe

    @parameterized.expand(
        [
            (
                0,
                "The planning timeframe cannot be 0 days.",
            ),
            (
                -1,
                "The planning timeframe cannot be a negative number of days.",
            ),
        ]
    )
    def test_that_invalid_timeframe_values_produce_correct_error_message_on_that_field(
        self, timeframe: int, expected_message: str
    ) -> None:
        form = self.create_form(timeframe=timeframe)
        self.controller.process_form(form=form, draft_id=uuid4())
        assert (
            self.translator.gettext(expected_message) in form.timeframe_field().errors
        )

    def test_that_user_id_from_session_is_used_for_editor_field(self) -> None:
        expected_id = uuid4()
        self.session.login_company(expected_id)
        request = self.controller.process_form(
            form=self.create_form(), draft_id=uuid4()
        )
        assert request
        assert request.editor == expected_id

    def test_no_request_is_returned_if_user_is_not_authenticated(self) -> None:
        self.session.logout()
        request = self.controller.process_form(
            form=self.create_form(), draft_id=uuid4()
        )
        assert request is None

    def test_that_draft_id_from_arguments_is_used_in_request(self) -> None:
        expected_draft_id = uuid4()
        request = self.controller.process_form(
            form=self.create_form(), draft_id=expected_draft_id
        )
        assert request
        assert request.draft == expected_draft_id

    def create_form(
        self,
        product_name: str = "test name",
        description: str = "test description",
        unit_of_distribution: str = "test unit",
        labour_cost: Decimal = Decimal(1),
        resource_cost: Decimal = Decimal(1),
        means_cost: Decimal = Decimal(1),
        amount: int = 1,
        is_public_service: bool = True,
        timeframe: int = 12,
    ) -> DraftForm:
        return DraftForm(
            prd_name=product_name,
            description=description,
            prd_unit=unit_of_distribution,
            costs_a=labour_cost,
            costs_p=means_cost,
            costs_r=resource_cost,
            prd_amount=amount,
            is_public_service=is_public_service,
            timeframe=timeframe,
        )
