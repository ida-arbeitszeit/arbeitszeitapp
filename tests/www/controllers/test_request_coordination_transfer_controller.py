from typing import Optional
from uuid import uuid4

from parameterized import parameterized

from arbeitszeit_web.www.controllers.request_coordination_transfer_controller import (
    RequestCoordinationTransferController,
)
from tests.forms import RequestCoordinationTransferFormImpl
from tests.www.base_test_case import BaseTestCase


class RequestCoordinationTransferControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(RequestCoordinationTransferController)

    @parameterized.expand([("invalid",), ("",), ("123",)])
    def test_that_none_gets_returned_if_candidate_field_in_form_is_invalid(
        self, candidate: str
    ) -> None:
        form = self.get_fake_form(candidate=candidate)
        self.assertIsNone(self.controller.import_form_data(form))

    @parameterized.expand([("invalid",), ("",), ("123",)])
    def test_that_none_gets_returned_if_requesting_tenure_field_in_form_is_invalid(
        self, requesting_tenure: str
    ) -> None:
        form = self.get_fake_form(requesting_tenure=requesting_tenure)
        self.assertIsNone(self.controller.import_form_data(form))

    def test_that_a_request_gets_returned_if_form_is_valid(self) -> None:
        form = self.get_fake_form()
        self.assertIsNotNone(self.controller.import_form_data(form))

    def test_that_request_has_candiate_specified_in_form(self) -> None:
        candidate = uuid4()
        form = self.get_fake_form(candidate=str(candidate))
        request = self.controller.import_form_data(form)
        assert request
        self.assertEqual(request.candidate, candidate)

    def test_that_request_has_tenure_specified_in_form(
        self,
    ) -> None:
        requesting_tenure = uuid4()
        form = self.get_fake_form(requesting_tenure=str(requesting_tenure))
        request = self.controller.import_form_data(form)
        assert request
        self.assertEqual(request.requesting_coordination_tenure, requesting_tenure)

    def get_fake_form(
        self, candidate: Optional[str] = None, requesting_tenure: Optional[str] = None
    ) -> RequestCoordinationTransferFormImpl:
        if candidate is None:
            candidate = str(uuid4())
        if requesting_tenure is None:
            requesting_tenure = str(uuid4())
        return RequestCoordinationTransferFormImpl(
            candidate=candidate, requesting_tenure=requesting_tenure
        )
