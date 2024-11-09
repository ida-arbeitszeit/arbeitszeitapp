from uuid import uuid4

from parameterized import parameterized

from arbeitszeit.records import ConsumptionType
from arbeitszeit_web.api.controllers.liquid_means_consumption_controller import (
    LiquidMeansConsumptionController,
    liquid_means_expected_inputs,
)
from arbeitszeit_web.api.controllers.parameters import FormParameter
from arbeitszeit_web.api.response_errors import BadRequest, Unauthorized
from tests.request import FakeRequest
from tests.www.base_test_case import BaseTestCase


class ControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(LiquidMeansConsumptionController)
        self.request = self.injector.get(FakeRequest)

    def test_controller_raises_unauthorized_for_anonymous_user(self) -> None:
        with self.assertRaises(Unauthorized):
            self.controller.create_request()

    def test_controller_raises_unauthorized_for_member(self) -> None:
        member = self.member_generator.create_member()
        self.session.login_member(member)
        with self.assertRaises(Unauthorized):
            self.controller.create_request()

    def test_controller_raises_unauthorized_for_accountant(self) -> None:
        accountant = self.accountant_generator.create_accountant()
        self.session.login_accountant(accountant)
        with self.assertRaises(Unauthorized):
            self.controller.create_request()

    def test_controller_raises_bad_request_when_plan_id_and_amount_are_missing(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.session.login_company(company)
        with self.assertRaises(BadRequest):
            self.controller.create_request()

    def test_controller_raises_bad_request_when_plan_id_is_missing(self) -> None:
        company = self.company_generator.create_company()
        self.session.login_company(company)
        self.request.set_json({"amount": "10"})
        with self.assertRaises(BadRequest):
            self.controller.create_request()

    def test_controller_raises_bad_request_when_amount_is_missing(self) -> None:
        company = self.company_generator.create_company()
        self.session.login_company(company)
        self.request.set_json({"plan_id": str(uuid4())})
        with self.assertRaises(BadRequest):
            self.controller.create_request()

    def test_controller_raises_bad_request_when_plan_id_is_not_in_uuid_format(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.session.login_company(company)
        self.request.set_json({"plan_id": "invalid_uuid", "amount": "10"})
        with self.assertRaises(BadRequest):
            self.controller.create_request()

    def test_controller_raises_bad_request_when_amount_is_a_character(self) -> None:
        company = self.company_generator.create_company()
        self.session.login_company(company)
        self.request.set_json({"plan_id": str(uuid4()), "amount": "invalid_amount"})
        with self.assertRaises(BadRequest):
            self.controller.create_request()

    def test_controller_raises_bad_request_when_amount_is_a_floating_number(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.session.login_company(company)
        self.request.set_json({"plan_id": str(uuid4()), "amount": "10.5"})
        with self.assertRaises(BadRequest):
            self.controller.create_request()

    def test_controller_raises_bad_request_when_amount_is_zero(self) -> None:
        company = self.company_generator.create_company()
        self.session.login_company(company)
        self.request.set_json({"plan_id": str(uuid4()), "amount": "0"})
        with self.assertRaises(BadRequest):
            self.controller.create_request()

    def test_controller_raises_bad_request_when_amount_is_negative(self) -> None:
        company = self.company_generator.create_company()
        self.session.login_company(company)
        self.request.set_json({"plan_id": str(uuid4()), "amount": "-10"})
        with self.assertRaises(BadRequest):
            self.controller.create_request()

    def test_controller_creates_request_with_consumer_set_to_currently_logged_in_company(
        self,
    ) -> None:
        expected_company = self.company_generator.create_company()
        self.session.login_company(expected_company)
        self.request.set_json({"plan_id": str(uuid4()), "amount": "10"})
        request = self.controller.create_request()
        self.assertEqual(request.consumer, expected_company)

    def test_controller_creates_request_with_plan_as_specified_in_post_body(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.session.login_company(company)
        expected_plan_id = uuid4()
        self.request.set_json({"plan_id": str(expected_plan_id), "amount": "10"})
        request = self.controller.create_request()
        self.assertEqual(request.plan, expected_plan_id)

    @parameterized.expand(
        [
            (1,),
            (101,),
            (1000,),
        ]
    )
    def test_controller_creates_request_with_amount_as_specified_in_post_body(
        self, expected_amount: int
    ) -> None:
        company = self.company_generator.create_company()
        self.session.login_company(company)
        self.request.set_json({"plan_id": str(uuid4()), "amount": str(expected_amount)})
        request = self.controller.create_request()
        self.assertEqual(request.amount, expected_amount)

    def test_controller_creates_request_with_consumption_type_set_to_raw_materials(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.session.login_company(company)
        self.request.set_json({"plan_id": str(uuid4()), "amount": "10"})
        request = self.controller.create_request()
        self.assertEqual(request.consumption_type, ConsumptionType.raw_materials)


class ExpectedInputsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(LiquidMeansConsumptionController)
        self.inputs = liquid_means_expected_inputs

    def test_controller_has_two_expected_inputs(self):
        self.assertEqual(len(self.inputs), 2)

    def test_first_expected_input_is_plan_id(self):
        input = self.inputs[0]
        self.assertEqual(input.name, "plan_id")

    def test_input_plan_id_is_of_type_form_param(self):
        input = self.inputs[0]
        assert isinstance(input, FormParameter)

    def test_input_plan_id_has_correct_parameters(self):
        input = self.inputs[0]
        self.assertEqual(input.name, "plan_id")
        self.assertEqual(input.type, str)
        self.assertEqual(input.description, "The plan to consume.")
        self.assertEqual(input.default, None)
        self.assertEqual(input.required, True)

    def test_second_expected_input_is_amount(self):
        input = self.inputs[1]
        self.assertEqual(input.name, "amount")

    def test_input_amount_is_of_type_form_param(self):
        input = self.inputs[1]
        assert isinstance(input, FormParameter)

    def test_input_amount_has_correct_parameters(self):
        input = self.inputs[1]
        self.assertEqual(input.name, "amount")
        self.assertEqual(input.type, int)
        self.assertEqual(input.description, "The amount of product to consume.")
        self.assertEqual(input.default, None)
        self.assertEqual(input.required, True)
