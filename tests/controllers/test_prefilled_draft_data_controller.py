from dataclasses import dataclass, replace
from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases import CreatePlanDraftRequest
from arbeitszeit_web.get_prefilled_draft_data import PrefilledDraftDataController
from tests.session import FakeSession

from .dependency_injection import get_dependency_injector


@dataclass
class FakeDraftForm:
    prd_name: str
    description: str
    timeframe: int
    prd_unit: str
    prd_amount: int
    costs_p: Decimal
    costs_r: Decimal
    costs_a: Decimal
    productive_or_public: str
    action: str

    def get_prd_name(self) -> str:
        return self.prd_name

    def get_description(self) -> str:
        return self.description

    def get_timeframe(self) -> int:
        return self.timeframe

    def get_prd_unit(self) -> str:
        return self.prd_unit

    def get_prd_amount(self) -> int:
        return self.prd_amount

    def get_costs_p(self) -> Decimal:
        return self.costs_p

    def get_costs_r(self) -> Decimal:
        return self.costs_r

    def get_costs_a(self) -> Decimal:
        return self.costs_a

    def get_productive_or_public(self) -> str:
        return self.productive_or_public

    def get_action(self) -> str:
        return self.action


class ControllerTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.session = self.injector.get(FakeSession)
        self.controller = self.injector.get(PrefilledDraftDataController)
        self.fake_form = FakeDraftForm(
            prd_name="test name",
            description="test description",
            timeframe=14,
            prd_unit="1 piece",
            prd_amount=10,
            costs_p=Decimal("10.5"),
            costs_r=Decimal("15"),
            costs_a=Decimal("20"),
            productive_or_public="public",
            action="save_draft",
        )
        self.session.set_current_user_id(uuid4())

    def test_import_of_data_returns_a_request_object(self):
        request = self.controller.import_form_data(self.fake_form)
        assert isinstance(request, CreatePlanDraftRequest)

    def test_import_of_data_transforms_prd_name_string_to_correct_string(self):
        assert isinstance(self.fake_form.prd_name, str)
        request = self.controller.import_form_data(self.fake_form)
        assert request.product_name == "test name"

    def test_import_of_data_transforms_description_string_to_correct_string(self):
        assert isinstance(self.fake_form.description, str)
        request = self.controller.import_form_data(self.fake_form)
        assert request.description == "test description"

    def test_import_of_data_transforms_timeframe_integer_to_correct_integer(self):
        assert isinstance(self.fake_form.timeframe, int)
        request = self.controller.import_form_data(self.fake_form)
        assert request.timeframe_in_days == 14

    def test_import_of_data_transforms_prd_unit_string_to_correct_string(self):
        assert isinstance(self.fake_form.prd_unit, str)
        request = self.controller.import_form_data(self.fake_form)
        assert request.production_unit == "1 piece"

    def test_import_of_data_transforms_prd_amount_integer_to_correct_integer(self):
        assert isinstance(self.fake_form.prd_amount, int)
        request = self.controller.import_form_data(self.fake_form)
        assert request.production_amount == 10

    def test_import_of_data_transforms_cost_decimals_to_correct_decimals(self):
        assert isinstance(self.fake_form.costs_p, Decimal)
        assert isinstance(self.fake_form.costs_r, Decimal)
        assert isinstance(self.fake_form.costs_a, Decimal)
        request = self.controller.import_form_data(self.fake_form)
        assert request.costs.means_cost == Decimal(10.5)
        assert request.costs.resource_cost == Decimal(15)
        assert request.costs.labour_cost == Decimal(20)

    def test_import_of_data_transforms_productive_or_public_string_to_correct_bool_when_public_service(
        self,
    ):
        assert isinstance(self.fake_form.productive_or_public, str)
        request = self.controller.import_form_data(self.fake_form)
        assert request.is_public_service == True

    def test_import_of_data_transforms_productive_or_public_string_to_correct_bool_when_productive(
        self,
    ):
        _fake_form = replace(self.fake_form, productive_or_public="productive")
        assert isinstance(_fake_form.productive_or_public, str)
        request = self.controller.import_form_data(_fake_form)
        assert request.is_public_service == False
