from uuid import uuid4

from arbeitszeit.use_cases import SendExtMessage, SendExtMessageRequest
from project.extensions import mail
from tests.data_generators import ExternalMessageGenerator

from .dependency_injection import injection_test


@injection_test
def test_sending_mail_is_successfull(
    send_ext_message: SendExtMessage, ext_msg_generator: ExternalMessageGenerator
):
    ext_message = ext_msg_generator.create_message(
        sender_adress="test_sender@cp.org",
        receiver_adress="test_receiver@cp.org",
        title="some subject",
        content_html="test html<br>test html",
    )
    request = SendExtMessageRequest(message_id=ext_message.id)
    with mail.record_messages() as outbox:
        response = send_ext_message(request)
        assert not response.is_rejected
        assert len(outbox) == 1
        assert outbox[0].sender == "test_sender@cp.org"
        assert outbox[0].recipients[0] == "test_receiver@cp.org"
        assert outbox[0].subject == "some subject"
        assert "<br>test" in outbox[0].html


@injection_test
def test_sending_mail_fails_if_message_does_not_exist(send_ext_message: SendExtMessage):
    request = SendExtMessageRequest(message_id=uuid4())
    with mail.record_messages() as outbox:
        response = send_ext_message(request)
        assert response.is_rejected
        assert len(outbox) == 0
