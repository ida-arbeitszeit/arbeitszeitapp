from typing import List

from arbeitszeit.injector import singleton
from arbeitszeit.presenters import NotifyAccountantsAboutNewPlanPresenter as Interface


@singleton
class NotifyAccountantsAboutNewPlanPresenterImpl:
    def __init__(self) -> None:
        self.sent_notifications: List[Interface.Notification] = []

    def notify_accountant_about_new_plan(
        self, notification: Interface.Notification
    ) -> None:
        self.sent_notifications.append(notification)

    @property
    def latest_notification(self) -> Interface.Notification:
        assert self.sent_notifications
        return self.sent_notifications[-1]
