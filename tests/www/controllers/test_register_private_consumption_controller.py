from typing import Optional
from uuid import uuid4

from parameterized import parameterized

from arbeitszeit.interactors.register_private_consumption import (
    RegisterPrivateConsumptionRequest,
)
from arbeitszeit_web.www.controllers.register_private_consumption_controller import (
    FormError,
    RegisterPrivateConsumptionController,
    ViewModel,
)
from arbeitszeit_web.www.response import Redirect
from tests.request import FakeRequest
from tests.www.base_test_case import BaseTestCase


class RegisterPrivateConsumptionControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(RegisterPrivateConsumptionController)
        self.session.login_member(uuid4())

    def test_error_is_returned_when_form_data_is_empty_strings(self) -> None:
        result = self._process_form(plan_id="", amount="")
        assert isinstance(result, FormError)

    def test_errors_message_when_amount_is_empty(self) -> None:
        result = self._process_form(amount="")
        assert isinstance(result, FormError)
        assert result.form.amount_errors == [
            self.translator.gettext("You must specify an amount.")
        ]

    def test_error_is_returned_when_plan_id_is_emtpy(self) -> None:
        result = self._process_form(plan_id="")
        assert isinstance(result, FormError)

    def test_error_is_returned_when_plan_id_is_not_a_valid_uuid(self) -> None:
        result = self._process_form(plan_id="1872da")
        assert isinstance(result, FormError)

    def test_error_is_returned_when_amount_is_empty(self) -> None:
        result = self._process_form(amount="")
        assert isinstance(result, FormError)

    def test_error_is_returned_when_amount_is_negative(self) -> None:
        result = self._process_form(amount="-1")
        assert isinstance(result, FormError)

    def test_error_is_returned_when_amount_is_zero(self) -> None:
        result = self._process_form(amount="0")
        assert isinstance(result, FormError)

    @parameterized.expand(
        [
            ("1.1",),
            ("-1.1",),
        ]
    )
    def test_error_is_returned_when_amount_is_a_floating_number(
        self, amount: str
    ) -> None:
        result = self._process_form(amount=amount)
        assert isinstance(result, FormError)

    def test_correct_error_message_returned_for_plan_id_when_form_data_is_empty_string(
        self,
    ) -> None:
        result = self._process_form(plan_id="", amount="")
        assert isinstance(result, FormError)
        assert result.form.plan_id_errors == [
            self.translator.gettext("Plan ID is invalid.")
        ]

    def test_correct_error_message_returned_when_plan_id_is_invalid_uuid(
        self,
    ) -> None:
        result = self._process_form(plan_id="aa18781hh")
        assert isinstance(result, FormError)
        assert result.form.plan_id_errors == [
            self.translator.gettext("Plan ID is invalid.")
        ]

    def test_correct_error_message_returned_when_amount_is_negative_int_string(
        self,
    ) -> None:
        result = self._process_form(amount="-1")
        assert isinstance(result, FormError)
        assert result.form.amount_errors == [
            self.translator.gettext("Must be a number larger than zero.")
        ]

    def test_correct_error_message_returned_when_amount_is_positive_float_string(
        self,
    ) -> None:
        result = self._process_form(amount="1.1")
        assert isinstance(result, FormError)
        assert result.form.amount_errors == [
            self.translator.gettext("This is not an integer."),
        ]

    def test_correct_error_message_returned_when_amount_is_negative_float_string(
        self,
    ) -> None:
        result = self._process_form(amount="-1.1")
        assert isinstance(result, FormError)
        assert result.form.amount_errors == [
            self.translator.gettext("This is not an integer."),
        ]

    def test_correct_error_message_returned_when_amount_string_contains_letters(
        self,
    ) -> None:
        result = self._process_form(amount="1a")
        assert isinstance(result, FormError)
        assert result.form.amount_errors == [
            self.translator.gettext("This is not an integer.")
        ]

    def test_that_amount_and_plan_id_field_have_errors_messages_when_both_are_empty(
        self,
    ) -> None:
        result = self._process_form(amount="", plan_id="")
        assert isinstance(result, FormError)
        assert result.form.plan_id_errors
        assert result.form.amount_errors

    def test_correct_amount_is_returned(self) -> None:
        result = self._process_form(amount="1234")
        assert isinstance(result, RegisterPrivateConsumptionRequest)
        self.assertEqual(result.amount, 1234)

    def test_correct_plan_uuid_is_returned(self) -> None:
        plan_uuid = uuid4()
        result = self._process_form(plan_id=str(plan_uuid))
        assert isinstance(result, RegisterPrivateConsumptionRequest)
        self.assertEqual(result.plan, plan_uuid)

    def test_correct_buyer_is_returned(self) -> None:
        buyer_uuid = uuid4()
        self.session.login_member(buyer_uuid)
        result = self._process_form()
        assert isinstance(result, RegisterPrivateConsumptionRequest)
        assert result.consumer == buyer_uuid

    def test_that_a_logged_out_user_is_redirected_to_the_member_login_page(
        self,
    ) -> None:
        self.session.logout()
        result = self._process_form()
        assert isinstance(result, Redirect)
        assert result.url == self.url_index.get_member_login_url()

    def _process_form(
        self,
        plan_id: Optional[str] = None,
        amount: Optional[str] = None,
    ) -> ViewModel:
        request = FakeRequest()
        if plan_id is None:
            request.set_form("plan_id", str(uuid4()))
        else:
            request.set_form("plan_id", plan_id)
        if amount is None:
            request.set_form("amount", "1")
        else:
            request.set_form("amount", amount)
        return self.controller.import_form_data(request=request)
