from uuid import uuid4

from parameterized import parameterized

from arbeitszeit.interactors import edit_draft
from arbeitszeit_web.forms import DraftForm
from arbeitszeit_web.www.controllers.edit_draft_controller import EditDraftController
from tests.request import FakeRequest
from tests.www.base_test_case import BaseTestCase

VALID_PRODUCT_NAME: str = "product name"
VALID_DESCRIPTION: str = "some description"
VALID_TIMEFRAME: str = "2"
VALID_PRD_UNIT: str = "1 piece"
VALID_PRD_AMOUNT: str = "10"
VALID_COSTS_P: str = "1.00"
VALID_COSTS_R: str = "2.00"
VALID_COSTS_A: str = "3.00"
VALID_IS_PUBLIC_PLAN: str = "on"


class EditDraftControllerTests(BaseTestCase):
    """
    Detailed tests of the validation process are not necessary, as the validation
    process is tested in the test suite for the CreateDraftController class.
    """

    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(EditDraftController)
        self.session.login_company(uuid4())
        self.draft_id = uuid4()

    def attach_form_data_to_request(
        self,
        request: FakeRequest,
        prd_name: str = VALID_PRODUCT_NAME,
        description: str = VALID_DESCRIPTION,
        timeframe: str = VALID_TIMEFRAME,
        prd_unit: str = VALID_PRD_UNIT,
        prd_amount: str = VALID_PRD_AMOUNT,
        costs_p: str = VALID_COSTS_P,
        costs_r: str = VALID_COSTS_R,
        costs_a: str = VALID_COSTS_A,
        is_public_plan: str = VALID_IS_PUBLIC_PLAN,
    ) -> FakeRequest:
        request.set_form("prd_name", prd_name)
        request.set_form("description", description)
        request.set_form("timeframe", timeframe)
        request.set_form("prd_unit", prd_unit)
        request.set_form("prd_amount", prd_amount)
        request.set_form("costs_p", costs_p)
        request.set_form("costs_r", costs_r)
        request.set_form("costs_a", costs_a)
        request.set_form("is_public_plan", is_public_plan)
        return request


class SuccessfulValidationTests(EditDraftControllerTests):
    def test_that_valid_form_data_is_converted_to_interactor_request(self) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request)
        interactor_request = self.controller.process_form(request, self.draft_id)
        assert isinstance(interactor_request, edit_draft.Request)

    def test_that_no_warning_is_displayed_if_form_data_is_valid(self) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request)
        self.controller.process_form(request, self.draft_id)
        assert not self.notifier.warnings

    @parameterized.expand(
        [
            "test name",
            "other test name",
        ]
    )
    def test_that_product_name_from_form_field_is_used_in_request(
        self, expected_name: str
    ) -> None:
        request = FakeRequest()
        request = self.attach_form_data_to_request(request, prd_name=expected_name)
        interactor_request = self.controller.process_form(request, self.draft_id)
        assert isinstance(interactor_request, edit_draft.Request)
        assert interactor_request.product_name == expected_name

    def test_that_user_id_from_session_is_used_for_editor_field(self) -> None:
        expected_id = uuid4()
        request = FakeRequest()
        self.session.login_company(expected_id)
        request = self.attach_form_data_to_request(FakeRequest())
        interactor_request = self.controller.process_form(request, self.draft_id)
        assert isinstance(interactor_request, edit_draft.Request)
        assert interactor_request.editor == expected_id

    def test_that_draft_id_from_arguments_is_used_in_request(self) -> None:
        expected_draft_id = uuid4()
        request = FakeRequest()
        request = self.attach_form_data_to_request(request)
        interactor_request = self.controller.process_form(request, expected_draft_id)
        assert isinstance(interactor_request, edit_draft.Request)
        assert interactor_request.draft == expected_draft_id


class UnsuccessfulValidationTests(EditDraftControllerTests):
    def test_that_invalid_form_data_is_converted_to_draft_form(self) -> None:
        request = FakeRequest()
        request.set_form("prd_name", "")
        draft_form = self.controller.process_form(request, self.draft_id)
        assert isinstance(draft_form, DraftForm)

    def test_that_correct_warning_is_displayed_if_form_data_is_invalid(self) -> None:
        request = FakeRequest()
        request.set_form("prd_name", "")
        self.controller.process_form(request, self.draft_id)
        assert len(self.notifier.warnings) == 1
        assert self.notifier.warnings[0] == self.translator.gettext(
            "Please correct the errors in the form."
        )
