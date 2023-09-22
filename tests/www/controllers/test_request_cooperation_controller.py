from dataclasses import dataclass, replace
from uuid import UUID, uuid4

from arbeitszeit.use_cases.request_cooperation import RequestCooperationRequest
from arbeitszeit_web.malformed_input_data import MalformedInputData
from arbeitszeit_web.www.controllers.request_cooperation_controller import (
    RequestCooperationController,
)
from tests.www.base_test_case import BaseTestCase


@dataclass
class FakeRequestCooperationForm:
    plan_id: str
    cooperation_id: str

    def get_plan_id_string(self) -> str:
        return self.plan_id

    def get_cooperation_id_string(self) -> str:
        return self.cooperation_id


fake_form = FakeRequestCooperationForm(
    plan_id=str(uuid4()), cooperation_id=str(uuid4())
)


class RequestCooperationControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(RequestCooperationController)

    def test_when_user_is_not_authenticated_then_we_cannot_get_a_use_case_request(
        self,
    ) -> None:
        self.session.logout()
        self.assertIsNone(self.controller.import_form_data(form=fake_form))

    def test_when_user_is_authenticated_then_the_user_is_identified_in_use_case_request(
        self,
    ) -> None:
        expected_user_id = uuid4()
        self.session.login_company(expected_user_id)
        use_case_request = self.controller.import_form_data(form=fake_form)
        assert use_case_request is not None
        assert isinstance(use_case_request, RequestCooperationRequest)
        self.assertEqual(use_case_request.requester_id, expected_user_id)

    def test_returns_malformed_data_instance_if_plan_id_cannot_be_converted_to_uuid(
        self,
    ):
        malformed_form = replace(fake_form, plan_id="malformed plan id")
        self.session.login_company(uuid4())
        use_case_request = self.controller.import_form_data(form=malformed_form)
        assert use_case_request is not None
        assert isinstance(use_case_request, MalformedInputData)
        self.assertEqual(use_case_request.field, "plan_id")
        self.assertEqual(
            use_case_request.message, self.translator.gettext("Invalid plan ID.")
        )

    def test_returns_malformed_data_instance_if_coop_id_cannot_be_converted_to_uuid(
        self,
    ):
        malformed_form = replace(fake_form, cooperation_id="malformed coop id")
        self.session.login_company(uuid4())
        use_case_request = self.controller.import_form_data(form=malformed_form)
        assert use_case_request is not None
        assert isinstance(use_case_request, MalformedInputData)
        self.assertEqual(use_case_request.field, "cooperation_id")
        self.assertEqual(
            use_case_request.message,
            self.translator.gettext("Invalid cooperation ID."),
        )

    def test_controller_can_convert_plan_and_cooperation_id_into_correct_uuid(self):
        self.session.login_company(uuid4())
        use_case_request = self.controller.import_form_data(form=fake_form)
        assert use_case_request is not None
        assert isinstance(use_case_request, RequestCooperationRequest)
        self.assertEqual(use_case_request.plan_id, UUID(fake_form.plan_id))
        self.assertEqual(
            use_case_request.cooperation_id, UUID(fake_form.cooperation_id)
        )
