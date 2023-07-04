from unittest import TestCase
from uuid import uuid4

from arbeitszeit.entities import PurposesOfPurchases
from arbeitszeit.use_cases.pay_means_of_production import PayMeansOfProductionRequest
from arbeitszeit_web.www.controllers.pay_means_of_production_controller import (
    PayMeansOfProductionController,
)
from tests.forms import PayMeansFakeForm
from tests.session import FakeSession
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector


class AuthenticatedCompanyTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.translator = self.injector.get(FakeTranslator)
        self.session = self.injector.get(FakeSession)
        self.expected_user_id = uuid4()
        self.session.login_company(self.expected_user_id)
        self.controller = PayMeansOfProductionController(self.session, self.translator)

    def test_use_case_request_gets_returned_when_correct_input_data(self):
        output = self.controller.process_input_data(self.get_fake_form())
        self.assertIsInstance(output, PayMeansOfProductionRequest)

    def test_successfull_use_case_request_has_correct_buyer_id(self):
        output = self.controller.process_input_data(self.get_fake_form())
        self.assertEqual(output.buyer, self.expected_user_id)

    def test_successfull_use_case_request_has_correct_plan_id(self):
        expected_plan_id = uuid4()
        output = self.controller.process_input_data(
            self.get_fake_form(plan_id=str(expected_plan_id))
        )
        self.assertEqual(output.plan, expected_plan_id)

    def test_successfull_use_case_request_has_plan_id_with_stripped_whitespaces(self):
        expected_plan_id = uuid4()
        form_input_plan_id = f"  {expected_plan_id}   "
        output = self.controller.process_input_data(
            self.get_fake_form(plan_id=form_input_plan_id)
        )
        self.assertEqual(output.plan, expected_plan_id)

    def test_successfull_use_case_request_has_correct_amount(self):
        expected_amount = 10
        output = self.controller.process_input_data(self.get_fake_form(amount="10"))
        self.assertEqual(output.amount, expected_amount)

    def test_successfull_use_case_request_has_correct_type_of_payment_of_fixed_means_of_production(
        self,
    ):
        expected_type_of_payment = PurposesOfPurchases.means_of_prod
        assert self.get_fake_form().type_of_payment_field().get_value() == "fixed"
        output = self.controller.process_input_data(self.get_fake_form())
        self.assertEqual(output.purpose, expected_type_of_payment)

    def test_successfull_use_case_request_has_correct_type_of_payment_of_liquid_means(
        self,
    ):
        expected_type_of_payment = PurposesOfPurchases.raw_materials
        output = self.controller.process_input_data(
            self.get_fake_form(type_of_payment="liquid")
        )
        self.assertEqual(output.purpose, expected_type_of_payment)

    def test_error_is_raised_if_amount_field_is_empty(self):
        with self.assertRaises(self.controller.FormError):
            self.controller.process_input_data(self.get_fake_form(amount=""))

    def test_error_is_raised_if_plan_id_field_is_empty(self):
        with self.assertRaises(self.controller.FormError):
            self.controller.process_input_data(self.get_fake_form(plan_id=""))

    def test_error_is_raised_if_type_of_payment_field_is_empty(self):
        with self.assertRaises(self.controller.FormError):
            self.controller.process_input_data(self.get_fake_form(type_of_payment=""))

    def test_correct_error_message_when_amount_is_negative(self):
        form = self.get_fake_form(amount="-1")
        with self.assertRaises(self.controller.FormError):
            self.controller.process_input_data(form)
        self.assertEqual(
            form.amount_field().errors,
            [self.translator.gettext("Must be a number larger than zero.")],
        )

    def test_correct_error_message_when_amount_is_float_string(self):
        form = self.get_fake_form(amount="1.1")
        with self.assertRaises(self.controller.FormError):
            self.controller.process_input_data(form)
        self.assertEqual(
            form.amount_field().errors,
            [self.translator.gettext("This is not an integer.")],
        )

    def test_correct_error_message_returned_when_amount_string_contains_letters(
        self,
    ) -> None:
        form = self.get_fake_form(amount="1a")
        with self.assertRaises(self.controller.FormError):
            self.controller.process_input_data(form)
        self.assertEqual(
            form.amount_field().errors,
            [self.translator.gettext("This is not an integer.")],
        )

    def test_correct_error_message_returned_for_plan_id_when_form_data_is_empty_string(
        self,
    ) -> None:
        form = self.get_fake_form(plan_id="")
        with self.assertRaises(self.controller.FormError):
            self.controller.process_input_data(form)
        self.assertEqual(
            form.plan_id_field().errors, [self.translator.gettext("Invalid ID.")]
        )

    def test_correct_error_message_returned_when_plan_id_is_invalid_uuid(
        self,
    ) -> None:
        form = self.get_fake_form(plan_id="aa18781hh")
        with self.assertRaises(self.controller.FormError):
            self.controller.process_input_data(form)
        self.assertEqual(
            form.plan_id_field().errors,
            [self.translator.gettext("Invalid ID.")],
        )

    def test_correct_error_message_returned_when_category_is_empty(
        self,
    ) -> None:
        form = self.get_fake_form(type_of_payment="")
        with self.assertRaises(self.controller.FormError):
            self.controller.process_input_data(form)
        self.assertEqual(
            form.type_of_payment_field().errors,
            [self.translator.gettext("This field is required.")],
        )

    def get_fake_form(
        self,
        amount: str = "10",
        plan_id: str = str(uuid4()),
        type_of_payment: str = "fixed",
    ) -> PayMeansFakeForm:
        return PayMeansFakeForm(
            amount=amount, plan_id=plan_id, type_of_payment=type_of_payment
        )
