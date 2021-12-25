from uuid import uuid4

from arbeitszeit.use_cases import SendExtMessage, SendExtMessageRequest
from tests.data_generators import ExternalMessageGenerator

from .dependency_injection import injection_test

DEFAULT_CREATE_ARGUMENTS = dict(
    sender_adress="test sender adress",
    receiver_adress="test receiver adress",
    title="test title",
    content_html="<p>some text</p>",
)


@injection_test
def test_message_with_random_id_gets_rejected(send_message: SendExtMessage):
    response = send_message(SendExtMessageRequest(message_id=uuid4()))
    assert response.is_rejected


@injection_test
def test_message_with_existing_id_can_be_sent(
    send_message: SendExtMessage, ext_msg_generator: ExternalMessageGenerator
):
    ext_message = ext_msg_generator.create_message(**DEFAULT_CREATE_ARGUMENTS)
    response = send_message(SendExtMessageRequest(message_id=ext_message.id))
    assert not response.is_rejected
