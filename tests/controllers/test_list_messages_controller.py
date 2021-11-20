from unittest import TestCase
from uuid import uuid4

from arbeitszeit_web.list_messages import ListMessagesController
from tests.flask_integration.session import FakeSession


class ListMessagesControllerTests(TestCase):
    def test_when_user_is_not_authenticated_then_we_cannot_get_a_use_case_request(
        self,
    ) -> None:
        session = FakeSession()
        controller = ListMessagesController(session=session)
        session.set_current_user_id(None)
        self.assertIsNone(controller.process_request_data())

    def test_when_user_is_authenticated_then_the_user_is_identified_in_use_case_request(
        self,
    ) -> None:
        session = FakeSession()
        controller = ListMessagesController(session=session)
        expected_user_id = uuid4()
        session.set_current_user_id(expected_user_id)
        use_case_request = controller.process_request_data()
        assert use_case_request is not None
        self.assertEqual(use_case_request.user, expected_user_id)
