from typing import Optional
from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.use_cases.pay_consumer_product import PayConsumerProductRequest
from arbeitszeit_web.pay_consumer_product import PayConsumerProductController
from tests.forms import PayConsumerProductFakeForm
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector

ControllerResult = Optional[PayConsumerProductRequest]


class PayConsumerProductControllerTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.translator = self.injector.get(FakeTranslator)
        self.controller = self.injector.get(PayConsumerProductController)
        self.form = PayConsumerProductFakeForm()

    def test_error_is_raised_when_form_data_is_empty_strings(self) -> None:
        with self.assertRaises(self.controller.FormError):
            self._process_form(plan_id="", amount="")

    def test_error_is_raised_when_plan_id_is_emtpy(self) -> None:
        with self.assertRaises(self.controller.FormError):
            self._process_form(plan_id="")

    def test_error_is_raised_when_plan_id_is_not_a_valid_uuid(self) -> None:
        with self.assertRaises(self.controller.FormError):
            self._process_form(plan_id="1872da")

    def test_error_is_raised_when_amount_is_empty(self) -> None:
        with self.assertRaises(self.controller.FormError):
            self._process_form(amount="")

    def test_error_is_raised_when_amount_is_negative(self) -> None:
        with self.assertRaises(self.controller.FormError):
            self._process_form(amount="-1")

    def test_error_is_raised_when_amount_is_zero(self) -> None:
        with self.assertRaises(self.controller.FormError):
            self._process_form(amount="0")

    def test_error_is_raised_when_amount_is_a_floating_number(self) -> None:
        for amount in ["1.1", "-1.1"]:
            with self.assertRaises(self.controller.FormError):
                self._process_form(amount=amount)

    def test_correct_error_message_returned_for_plan_id_when_form_data_is_empty_string(
        self,
    ) -> None:
        with self.assertRaises(self.controller.FormError):
            self._process_form(plan_id="", amount="")
        self.assertEqual(
            self.form.plan_id_errors, [self.translator.gettext("Plan ID is invalid.")]
        )

    def test_correct_error_message_returned_when_plan_id_is_invalid_uuid(
        self,
    ) -> None:
        with self.assertRaises(self.controller.FormError):
            self._process_form(plan_id="aa18781hh")
        self.assertEqual(
            self.form.plan_id_errors,
            [self.translator.gettext("Plan ID is invalid.")],
        )

    def test_correct_error_message_returned_when_amount_is_negative_int_string(
        self,
    ) -> None:
        with self.assertRaises(self.controller.FormError):
            self._process_form(amount="-1")
        self.assertEqual(
            self.form.amount_errors,
            [self.translator.gettext("Must be a number larger than zero.")],
        )

    def test_correct_error_message_returned_when_amount_is_positive_float_string(
        self,
    ) -> None:
        with self.assertRaises(self.controller.FormError):
            self._process_form(amount="1.1")
        self.assertEqual(
            self.form.amount_errors,
            [
                self.translator.gettext("This is not an integer."),
            ],
        )

    def test_correct_error_message_returned_when_amount_is_negative_float_string(
        self,
    ) -> None:
        with self.assertRaises(self.controller.FormError):
            self._process_form(amount="-1.1")
        self.assertEqual(
            self.form.amount_errors,
            [
                self.translator.gettext("This is not an integer."),
            ],
        )

    def test_correct_error_message_returned_when_amount_string_contains_letters(
        self,
    ) -> None:
        with self.assertRaises(self.controller.FormError):
            self._process_form(amount="1a")
        self.assertEqual(
            self.form.amount_errors,
            [self.translator.gettext("This is not an integer.")],
        )

    def test_valid_data_returned_when_uuid_is_valid_and_amount_is_number(self):
        result = self._process_form()
        self.assertTrue(result)

    def test_correct_amount_is_returned(self) -> None:
        result = self._process_form(amount="1234")
        assert result
        self.assertEqual(result.amount, 1234)

    def test_correct_plan_uuid_is_returned(self) -> None:
        plan_uuid = uuid4()
        result = self._process_form(plan_id=str(plan_uuid))
        assert result
        self.assertEqual(result.plan, plan_uuid)

    def test_correct_buyer_is_returned(self) -> None:
        buyer_uuid = uuid4()
        result = self._process_form(buyer=buyer_uuid)
        assert result
        self.assertEqual(result.buyer, buyer_uuid)

    def _process_form(
        self,
        buyer: Optional[UUID] = None,
        plan_id: Optional[str] = None,
        amount: Optional[str] = None,
    ) -> ControllerResult:
        if plan_id is None:
            plan_id = str(uuid4())
        if amount is None:
            amount = "1"
        self.form.set_amount(amount)
        self.form.set_plan_id(plan_id)
        return self.controller.import_form_data(
            current_user=uuid4() if buyer is None else buyer,
            form=self.form,
        )
