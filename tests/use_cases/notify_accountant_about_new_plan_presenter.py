from typing import List

from injector import singleton

from arbeitszeit.accountant_notifications import Notification


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
