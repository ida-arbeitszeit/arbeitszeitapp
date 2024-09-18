from typing import Optional
from uuid import UUID, uuid4

import pytest

from arbeitszeit.use_cases.register_private_consumption import (
    RegisterPrivateConsumptionRequest,
)
from arbeitszeit_web.www.controllers.register_private_consumption_controller import (
    RegisterPrivateConsumptionController,
)
from tests.request import FakeRequest
from tests.www.base_test_case import BaseTestCase

ControllerResult = Optional[RegisterPrivateConsumptionRequest]


class RegisterPrivateConsumptionControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(RegisterPrivateConsumptionController)

    def test_error_is_raised_when_form_data_is_empty_strings(self) -> None:
        with self.assertRaises(self.controller.FormError):
            self._process_form(plan_id="", amount="")

    def test_errors_message_when_amount_is_empty(self) -> None:
        with pytest.raises(self.controller.FormError) as error:
            self._process_form(amount="")
        assert error.value.form.amount_errors == [
            self.translator.gettext("You must specify an amount.")
        ]

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
        with pytest.raises(self.controller.FormError) as error:
            self._process_form(plan_id="", amount="")
        assert error.value.form.plan_id_errors == [
            self.translator.gettext("Plan ID is invalid.")
        ]

    def test_correct_error_message_returned_when_plan_id_is_invalid_uuid(
        self,
    ) -> None:
        with pytest.raises(self.controller.FormError) as error:
            self._process_form(plan_id="aa18781hh")
        assert error.value.form.plan_id_errors == [
            self.translator.gettext("Plan ID is invalid.")
        ]

    def test_correct_error_message_returned_when_amount_is_negative_int_string(
        self,
    ) -> None:
        with pytest.raises(self.controller.FormError) as error:
            self._process_form(amount="-1")
        assert error.value.form.amount_errors == [
            self.translator.gettext("Must be a number larger than zero.")
        ]

    def test_correct_error_message_returned_when_amount_is_positive_float_string(
        self,
    ) -> None:
        with pytest.raises(self.controller.FormError) as error:
            self._process_form(amount="1.1")
        assert error.value.form.amount_errors == [
            self.translator.gettext("This is not an integer."),
        ]

    def test_correct_error_message_returned_when_amount_is_negative_float_string(
        self,
    ) -> None:
        with pytest.raises(self.controller.FormError) as error:
            self._process_form(amount="-1.1")
        assert error.value.form.amount_errors == [
            self.translator.gettext("This is not an integer."),
        ]

    def test_correct_error_message_returned_when_amount_string_contains_letters(
        self,
    ) -> None:
        with pytest.raises(self.controller.FormError) as error:
            self._process_form(amount="1a")
        assert error.value.form.amount_errors == [
            self.translator.gettext("This is not an integer.")
        ]

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
        self.assertEqual(result.consumer, buyer_uuid)

    def _process_form(
        self,
        buyer: Optional[UUID] = None,
        plan_id: Optional[str] = None,
        amount: Optional[str] = None,
    ) -> ControllerResult:
        request = FakeRequest()
        if plan_id is None:
            request.set_form("plan_id", str(uuid4()))
        else:
            request.set_form("plan_id", plan_id)
        if amount is None:
            request.set_form("amount", "1")
        else:
            request.set_form("amount", amount)
        return self.controller.import_form_data(
            current_user=uuid4() if buyer is None else buyer,
            request=request,
        )
