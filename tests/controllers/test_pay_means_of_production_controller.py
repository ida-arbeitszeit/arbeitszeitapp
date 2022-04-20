from typing import Dict, List
from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.entities import PurposesOfPurchases
from arbeitszeit.use_cases.pay_means_of_production import PayMeansOfProductionRequest
from arbeitszeit_web.controllers.pay_means_of_production_controller import (
    PayMeansOfProductionController,
)
from tests.request import FakeRequest
from tests.session import FakeSession


class FakePayMeansForm:
    def __init__(self, amount: int, plan_id: str, category: str) -> None:
        self.amount = amount
        self.plan_id = plan_id
        self.category = category
        self._errors: Dict[str, List[str]] = {}
        self.validate()

    def get_amount_field(self) -> int:
        return self.amount

    def get_plan_id_field(self) -> str:
        return self.plan_id.strip()

    def get_category_field(self) -> str:
        return self.category

    def validate(self) -> bool:
        if self.get_amount_field() < 0:
            self._errors["amount"] = ["Must be minimum 0."]
            return False
        try:
            UUID(self.get_plan_id_field())
        except ValueError:
            self._errors["plan_id"] = ["No valid UUID."]
            return False
        return True

    @property
    def errors(self) -> Dict:
        return self._errors


class AuthenticatedCompanyTests(TestCase):
    def setUp(self) -> None:
        self.session = FakeSession()
        self.request = FakeRequest()
        self.controller = PayMeansOfProductionController(self.session, self.request)
        self.expected_user_id = uuid4()
        self.session.set_current_user_id(self.expected_user_id)
        self.fake_form = FakePayMeansForm(
            amount=10, plan_id=str(uuid4()), category="Fixed"
        )

    def test_use_case_request_gets_returned_when_correct_input_data(self):
        output = self.controller.process_input_data(self.fake_form)
        self.assertIsInstance(output, PayMeansOfProductionRequest)

    def test_successfull_use_case_request_has_correct_buyer_id(self):
        output = self.controller.process_input_data(self.fake_form)
        assert isinstance(output, PayMeansOfProductionRequest)
        self.assertEqual(output.buyer, self.expected_user_id)

    def test_successfull_use_case_request_has_correct_plan_id(self):
        expected_plan_id = UUID(self.fake_form.plan_id)
        output = self.controller.process_input_data(self.fake_form)
        assert isinstance(output, PayMeansOfProductionRequest)
        self.assertEqual(output.plan, expected_plan_id)

    def test_successfull_use_case_request_has_correct_amount(self):
        expected_amount = self.fake_form.amount
        output = self.controller.process_input_data(self.fake_form)
        assert isinstance(output, PayMeansOfProductionRequest)
        self.assertEqual(output.amount, expected_amount)

    def test_successfull_use_case_request_has_correct_category_of_fixed_means_of_production(
        self,
    ):
        expected_category = PurposesOfPurchases.means_of_prod
        assert self.fake_form.category == "Fixed"
        output = self.controller.process_input_data(self.fake_form)
        assert isinstance(output, PayMeansOfProductionRequest)
        self.assertEqual(output.purpose, expected_category)

    def test_successfull_use_case_request_has_correct_category_of_liquid_means(self):
        expected_category = PurposesOfPurchases.raw_materials
        form = self.fake_form
        form.category = "Liquid"
        output = self.controller.process_input_data(self.fake_form)
        assert isinstance(output, PayMeansOfProductionRequest)
        self.assertEqual(output.purpose, expected_category)

    def test_correct_malformed_data_object_is_returned_when_form_has_malformed_plan_uuid(
        self,
    ):
        form = self.fake_form
        form.plan_id = "malformed"
        output = self.controller.process_input_data(form)
        assert isinstance(output, PayMeansOfProductionController.MalformedInputData)
        self.assertTrue(output.field_messages.get("plan_id"))

    def test_correct_malformed_data_object_is_returned_when_form_has_negative_amount(
        self,
    ):
        form = self.fake_form
        form.amount = -10
        output = self.controller.process_input_data(form)
        assert isinstance(output, PayMeansOfProductionController.MalformedInputData)
        self.assertTrue(output.field_messages.get("amount"))
        self.assertFalse(output.field_messages.get("plan_id"))
