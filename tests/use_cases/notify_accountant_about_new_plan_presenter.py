from typing import List

from arbeitszeit.accountant_notifications import Notification
from arbeitszeit.injector import singleton


@singleton
class NotifyAccountantsAboutNewPlanPresenterImpl:
    def __init__(self) -> None:
        self.sent_notifications: List[Notification] = []

    def notify_accountant_about_new_plan(self, notification: Notification) -> None:
        self.sent_notifications.append(notification)

    @property
    def latest_notification(self) -> Notification:
        assert self.sent_notifications
        return self.sent_notifications[-1]
