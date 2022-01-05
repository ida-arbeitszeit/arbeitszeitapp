# This pattern will be used in the next commit, then deleted

# from arbeitszeit.use_cases import SendExtMessage, SendExtMessageRequest
# from project.extensions import mail

# from .dependency_injection import injection_test


# @injection_test
# def test_sending_mail_is_successfull(send_ext_message: SendExtMessage):
#     request = SendExtMessageRequest(
#         sender_adress="test_sender@cp.org",
#         receiver_adress="test_receiver@cp.org",
#         title="some subject",
#         content_html="test html<br>test html",
#     )
#     with mail.record_messages() as outbox:
#         response = send_ext_message(request)
#         assert not response.is_rejected
#         assert len(outbox) == 1
#         assert outbox[0].sender == "test_sender@cp.org"
#         assert outbox[0].recipients[0] == "test_receiver@cp.org"
#         assert outbox[0].subject == "some subject"
#         assert "<br>test" in outbox[0].html
