from uuid import uuid4

from tests.data_generators import MemberGenerator, WorkerInviteMessageGenerator

from .flask import ViewTestCase


class MemberViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member_generator = self.injector.get(MemberGenerator)
        self.message_generator = self.injector.get(WorkerInviteMessageGenerator)
        self.member, _, self.email = self.login_member()
        self.member = self.confirm_member(member=self.member, email=self.email)

    def test_get_302_when_message_exists(self) -> None:
        message = self.message_generator.create_message(worker=self.member)
        url = f"/member/worker_invite_messages/{message.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_get_404_when_message_does_not_exist(self) -> None:
        response = self.client.get(f"/member/worker_invite_messages/{uuid4()}")
        self.assertEqual(response.status_code, 404)

    def test_get_404_when_message_is_not_addressed_to_current_worker(self) -> None:
        other_worker = self.member_generator.create_member()
        message = self.message_generator.create_message(worker=other_worker)
        url = f"/member/messworker_invite_messagesges/{message.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
