from dataclasses import dataclass
from typing import Optional, Union
from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit_web.pay_consumer_product import (
    PayConsumerProductController,
    PayConsumerProductRequestImpl,
)

ControllerResult = Union[
    PayConsumerProductRequestImpl,
    PayConsumerProductController.MalformedInputData,
]


class PayConsumerProductControllerTests(TestCase):
    def setUp(self) -> None:
        self.controller = PayConsumerProductController()

    def test_malformed_data_is_returned_when_form_data_is_empty_strings(self) -> None:
        result = self._process_form(plan_id="", amount="")
        self._assert_malformed_data(result)

    def test_malformed_data_is_returned_when_plan_uuid_is_not_valid(self) -> None:
        result = self._process_form(plan_id="123")
        self._assert_malformed_field(
            result, field="plan_id", message="Plan-ID ist ungültig"
        )

    def test_malformed_data_is_returned_when_amount_contains_letters(self) -> None:
        result = self._process_form(amount="1a")
        self._assert_malformed_field(
            result, "amount", message="Das ist keine ganze Zahl"
        )

    def test_valid_data_returned_when_uuid_is_valid_and_amount_is_number(self):
        result = self._process_form()
        self.assertIsInstance(
            result,
            PayConsumerProductRequestImpl,
        )

    def test_correct_amount_is_returned(self) -> None:
        result = self._process_form(amount="1234")
        self._assert_amount(result, 1234)

    def test_correct_plan_uuid_is_returned(self) -> None:
        plan_uuid = uuid4()
        result = self._process_form(plan_id=str(plan_uuid))
        self._assert_plan_uuid(result, plan_uuid)

    def test_correct_buyer_is_returned(self) -> None:
        buyer_uuid = uuid4()
        result = self._process_form(buyer=buyer_uuid)
        self._assert_buyer_uuid(result, buyer_uuid)

    def _assert_buyer_uuid(
        self,
        result: ControllerResult,
        buyer: UUID,
    ):
        assert isinstance(result, PayConsumerProductRequestImpl)
        self.assertEqual(result.get_buyer_id(), buyer)

    def _assert_malformed_data(
        self,
        result: ControllerResult,
    ) -> None:
        self.assertIsInstance(result, PayConsumerProductController.MalformedInputData)

    def _assert_amount(
        self,
        result: ControllerResult,
        amount: int,
    ) -> None:
        assert isinstance(result, PayConsumerProductRequestImpl)
        self.assertEqual(result.get_amount(), amount)

    def _assert_plan_uuid(
        self,
        result: ControllerResult,
        plan_uuid: UUID,
    ):
        assert isinstance(result, PayConsumerProductRequestImpl)
        self.assertEqual(result.get_plan_id(), plan_uuid)

    def _assert_malformed_field(
        self,
        result: ControllerResult,
        field: str,
        message: Optional[str] = None,
    ):
        assert isinstance(result, PayConsumerProductController.MalformedInputData)
        assert result.field == field
        if message is not None:
            self.assertEqual(result.message, message)

    def _process_form(
        self,
        buyer: Optional[UUID] = None,
        plan_id: Optional[str] = None,
        amount: str = "1",
    ) -> ControllerResult:
        return self.controller.import_form_data(
            uuid4() if buyer is None else buyer,
            PayConsumerProductFakeForm(
                plan_id=str(uuid4()) if plan_id is None else plan_id,
                amount=amount,
            ),
        )


@dataclass
class PayConsumerProductFakeForm:
    plan_id: str
    amount: str

    def get_plan_id_field(self) -> str:
        return self.plan_id

    def get_amount_field(self) -> str:
        return self.amount
