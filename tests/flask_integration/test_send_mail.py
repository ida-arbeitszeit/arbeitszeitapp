from arbeitszeit.repositories import SentExternalMessageRepository
from arbeitszeit.use_cases import SendExtMessage, SendExtMessageRequest
from project.extensions import mail

from .dependency_injection import injection_test


@injection_test
def test_sending_mail_is_successfull(send_ext_message: SendExtMessage):
    request = SendExtMessageRequest(
        sender_adress="test_sender@cp.org",
        receiver_adress="test_receiver@cp.org",
        title="some subject",
        content_html="test html<br>test html",
    )
    with mail.record_messages() as outbox:
        response = send_ext_message(request)
        assert not response.is_rejected
        assert len(outbox) == 1
        assert outbox[0].sender == "test_sender@cp.org"
        assert outbox[0].recipients[0] == "test_receiver@cp.org"
        assert outbox[0].subject == "some subject"
        assert "<br>test" in outbox[0].html


@injection_test
def test_successfully_sent_mail_is_saved_in_database(
    send_ext_message: SendExtMessage, repo: SentExternalMessageRepository
):
    request = SendExtMessageRequest(
        sender_adress="test_sender@cp.org",
        receiver_adress="test_receiver@cp.org",
        title="some subject",
        content_html="test html<br>test html",
    )
    response = send_ext_message(request)
    assert response.sent_message is not None
    saved_message = repo.get_by_id(response.sent_message)
    assert saved_message
    assert saved_message.title == request.title
