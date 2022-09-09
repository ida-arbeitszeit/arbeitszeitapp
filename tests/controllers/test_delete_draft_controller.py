from unittest import TestCase
from uuid import uuid4

from arbeitszeit_web.controllers.delete_draft_controller import DeleteDraftController
from tests.session import FakeSession

from .dependency_injection import get_dependency_injector


class ControllerTests(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.injector = get_dependency_injector()
        self.session = self.injector.get(FakeSession)
        self.controller = self.injector.get(DeleteDraftController)

    def test_that_deleter_is_current_user(self) -> None:
        expected_deleter = uuid4()
        self.session.set_current_user_id(expected_deleter)
        request = self.controller.get_request(uuid4())
        self.assertEqual(request.deleter, expected_deleter)

    def test_that_draft_is_taken_from_argument(self) -> None:
        expected_draft = uuid4()
        self.session.set_current_user_id(uuid4())
        request = self.controller.get_request(expected_draft)
        self.assertEqual(request.draft, expected_draft)

    def test_that_failure_exception_is_risen_when_user_is_not_authenticated(
        self,
    ) -> None:
        with self.assertRaises(DeleteDraftController.Failure):
            request = self.controller.get_request(uuid4())
