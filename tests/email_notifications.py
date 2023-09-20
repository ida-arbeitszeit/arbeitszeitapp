from arbeitszeit import email_notifications as interface


class EmailSenderTestImpl:
    def __init__(self) -> None:
        self._sent_messages: list[interface.Message] = []

    def send_email(self, message: interface.Message) -> None:
        self._sent_messages.append(message)

    def get_latest_message_sent(self) -> interface.Message:
        assert (
            self._sent_messages
        ), "Did not have any sent messages although the latest message sent was requested"
        return self._sent_messages[-1]

    def get_messages_sent(self) -> list[interface.Message]:
        return list(self._sent_messages)
