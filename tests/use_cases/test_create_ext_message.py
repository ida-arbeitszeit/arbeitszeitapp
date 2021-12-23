from arbeitszeit.use_cases import CreateExtMessage, CreateExtMessageRequest

from .dependency_injection import injection_test

DEFAULT_CREATE_ARGUMENTS = dict(
    sender_adress="test sender adress",
    receiver_adress="test receiver adress",
    title="test title",
    content="some text",
)


@injection_test
def test_message_can_be_created(create_message: CreateExtMessage):
    response = create_message(CreateExtMessageRequest(**DEFAULT_CREATE_ARGUMENTS))
    assert not response.is_rejected
    assert response.message_id
