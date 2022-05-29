from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases import ReadWorkerInviteMessage
from arbeitszeit_web.read_worker_invite_message import ReadWorkerInviteMessagePresenter

from .dependency_injection import get_dependency_injector


class ReadWorkerInviteMessagePresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.presenter = self.injector.get(ReadWorkerInviteMessagePresenter)

    def test_invite_id_is_shown_in_view_model(self) -> None:
        invite_id = uuid4()
        use_case_response = ReadWorkerInviteMessage.Success(
            invite_id=invite_id,
        )
        view_model = self.presenter.present(use_case_response)
        self.assertEqual(view_model.invite_id, str(invite_id))
