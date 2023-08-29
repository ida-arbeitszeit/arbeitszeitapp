from arbeitszeit.injector import singleton
from arbeitszeit.presenters import ChangeUserEmailAddressPresenter as Interface


@singleton
class ChangeUserEmailAddressPresenterMock:
    def __init__(self) -> None:
        self._notifications: list[Interface.Notification] = list()

    def present_email_change_confirmation_message(
        self, notification: Interface.Notification
    ) -> None:
        self._notifications.append(notification)

    def has_notifications_delivered(self) -> bool:
        return bool(self._notifications)

    def get_latest_notification_delivered(self) -> Interface.Notification:
        assert self._notifications
        return self._notifications[-1]
