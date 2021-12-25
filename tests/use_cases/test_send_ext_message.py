from arbeitszeit.repositories import SentExternalMessageRepository
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
    assert response.sent_message is not None


@injection_test
def test_message_is_saved_in_db_after_sending(
    send_message: SendExtMessage, repo: SentExternalMessageRepository
):
    response = send_message(SendExtMessageRequest(**DEFAULT_SEND_ARGUMENTS))
    assert not response.is_rejected
    assert response.sent_message
    sent_message = repo.get_by_id(response.sent_message)
    assert sent_message is not None
    assert sent_message.title == "test title"
