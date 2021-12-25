from arbeitszeit.use_cases import SendExtMessage, SendExtMessageRequest

from .dependency_injection import injection_test

DEFAULT_SEND_ARGUMENTS = dict(
    sender_adress="test sender adress",
    receiver_adress="test receiver adress",
    title="test title",
    content_html="<p>some text</p>",
)


@injection_test
def test_message_can_be_sent(send_message: SendExtMessage):
    response = send_message(SendExtMessageRequest(**DEFAULT_SEND_ARGUMENTS))
    assert not response.is_rejected
