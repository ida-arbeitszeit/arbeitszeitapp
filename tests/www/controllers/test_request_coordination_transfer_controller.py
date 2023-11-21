from typing import Optional
from uuid import uuid4

from parameterized import parameterized

from arbeitszeit_web.www.controllers.request_coordination_transfer_controller import (
    RequestCoordinationTransferController,
)
from tests.forms import RequestCoordinationTransferFormImpl
from tests.www.base_test_case import BaseTestCase


class AuthenticatedCompanyTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(RequestCoordinationTransferController)
        self.company = self.company_generator.create_company()
        self.session.login_company(company=self.company)

    @parameterized.expand([("invalid",), ("",), ("123",)])
    def test_that_none_gets_returned_if_candidate_field_in_form_is_invalid(
        self, candidate: str
    ) -> None:
        form = self.get_fake_form(candidate=candidate)
        self.assertIsNone(self.controller.import_form_data(form))

    def test_that_candidate_field_has_error_attached_if_field_is_invalid(
        self,
    ) -> None:
        form = self.get_fake_form(candidate="invalid")
        self.controller.import_form_data(form)
        self.assertTrue(form.candidate_field().errors)

    @parameterized.expand([("invalid",), ("",), ("123",)])
    def test_that_none_gets_returned_if_cooperation_field_in_form_is_invalid(
        self, cooperation: str
    ) -> None:
        form = self.get_fake_form(cooperation=cooperation)
        self.assertIsNone(self.controller.import_form_data(form))

    def test_that_cooperation_field_has_error_attached_if_field_is_invalid(
        self,
    ) -> None:
        form = self.get_fake_form(cooperation="invalid")
        self.controller.import_form_data(form)
        self.assertTrue(form.cooperation_field().errors)

    def test_that_a_request_gets_returned_if_form_is_valid(self) -> None:
        form = self.get_fake_form()
        self.assertIsNotNone(self.controller.import_form_data(form))

    def test_that_request_has_candiate_specified_in_form(self) -> None:
        candidate = uuid4()
        form = self.get_fake_form(candidate=str(candidate))
        request = self.controller.import_form_data(form)
        assert request
        self.assertEqual(request.candidate, candidate)

    def test_that_request_has_cooperation_specified_in_form(
        self,
    ) -> None:
        cooperation = uuid4()
        form = self.get_fake_form(cooperation=str(cooperation))
        request = self.controller.import_form_data(form)
        assert request
        self.assertEqual(request.cooperation, cooperation)

    def test_that_request_has_current_user_as_requester_in_request(self) -> None:
        form = self.get_fake_form()
        request = self.controller.import_form_data(form)
        assert request
        self.assertEqual(request.requester, self.company)

    def get_fake_form(
        self, candidate: Optional[str] = None, cooperation: Optional[str] = None
    ) -> RequestCoordinationTransferFormImpl:
        if candidate is None:
            candidate = str(uuid4())
        if cooperation is None:
            cooperation = str(uuid4())
        return RequestCoordinationTransferFormImpl(
            candidate=candidate, cooperation=cooperation
        )
