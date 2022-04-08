from dataclasses import dataclass, replace
from decimal import Decimal
from uuid import uuid4

from arbeitszeit.use_cases import CreatePlanDraftRequest
from arbeitszeit_web.get_prefilled_draft_data import PrefilledDraftDataController
from tests.session import FakeSession


@dataclass
class FakeDraftForm:
    prd_name: str
    description: str
    timeframe: str
    prd_unit: str
    prd_amount: str
    costs_p: str
    costs_r: str
    costs_a: str
    productive_or_public: str
    action: str

    def get_prd_name_string(self) -> str:
        return self.prd_name

    def get_description_string(self) -> str:
        return self.description

    def get_timeframe_string(self) -> str:
        return self.timeframe

    def get_prd_unit_string(self) -> str:
        return self.prd_unit

    def get_prd_amount_string(self) -> str:
        return self.prd_amount

    def get_costs_p_string(self) -> str:
        return self.costs_p

    def get_costs_r_string(self) -> str:
        return self.costs_r

    def get_costs_a_string(self) -> str:
        return self.costs_a

    def get_productive_or_public_string(self) -> str:
        return self.productive_or_public

    def get_action_string(self) -> str:
        return self.action


fake_form = FakeDraftForm(
    prd_name="test name",
    description="test description",
    timeframe="14",
    prd_unit="1 piece",
    prd_amount="10",
    costs_p="10.5",
    costs_r="15",
    costs_a="20",
    productive_or_public="public",
    action="save_draft",
)

session = FakeSession()
session.set_current_user_id(uuid4())
controller = PrefilledDraftDataController(session)


def test_import_of_data_returns_a_request_object():
    request = controller.import_form_data(fake_form)
    assert isinstance(request, CreatePlanDraftRequest)


def test_import_of_data_transforms_prd_name_string_to_correct_string():
    assert isinstance(fake_form.prd_name, str)
    request = controller.import_form_data(fake_form)
    assert request.product_name == "test name"


def test_import_of_data_transforms_description_string_to_correct_string():
    assert isinstance(fake_form.description, str)
    request = controller.import_form_data(fake_form)
    assert request.description == "test description"


def test_import_of_data_transforms_timeframe_string_to_correct_integer():
    assert isinstance(fake_form.timeframe, str)
    request = controller.import_form_data(fake_form)
    assert request.timeframe_in_days == 14


def test_import_of_data_transforms_prd_unit_string_to_correct_string():
    assert isinstance(fake_form.prd_unit, str)
    request = controller.import_form_data(fake_form)
    assert request.production_unit == "1 piece"


def test_import_of_data_transforms_prd_amount_string_to_correct_integer():
    assert isinstance(fake_form.prd_amount, str)
    request = controller.import_form_data(fake_form)
    assert request.production_amount == 10


def test_import_of_data_transforms_cost_strings_to_correct_decimal():
    assert isinstance(fake_form.costs_p, str)
    assert isinstance(fake_form.costs_r, str)
    assert isinstance(fake_form.costs_a, str)
    request = controller.import_form_data(fake_form)
    assert request.costs.means_cost == Decimal(10.5)
    assert request.costs.resource_cost == Decimal(15)
    assert request.costs.labour_cost == Decimal(20)


def test_import_of_data_transforms_productive_or_public_string_to_correct_bool_when_public_service():
    assert isinstance(fake_form.productive_or_public, str)
    request = controller.import_form_data(fake_form)
    assert request.is_public_service == True


def test_import_of_data_transforms_productive_or_public_string_to_correct_bool_when_productive():
    _fake_form = replace(fake_form, productive_or_public="productive")
    assert isinstance(_fake_form.productive_or_public, str)
    request = controller.import_form_data(_fake_form)
    assert request.is_public_service == False
