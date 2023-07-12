"""This module contains interfaces for presenters that don't fit into
a simple request response model.
"""
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


class MemberRegistrationMessagePresenter(Protocol):
    def show_member_registration_message(self, email_address: str) -> None:
        ...


class CompanyRegistrationMessagePresenter(Protocol):
    def show_company_registration_message(self, email_address: str) -> None:
        ...


class NotifyAccountantsAboutNewPlanPresenter(Protocol):
    @dataclass
    class Notification:
        product_name: str
        plan_id: UUID
        accountant_id: UUID

    def notify_accountant_about_new_plan(self, notification: Notification) -> None:
        ...


class AccountantInvitationPresenter(Protocol):
    def send_accountant_invitation(self, email: str) -> None:
        ...


class InviteWorkerPresenter(Protocol):
    def show_invite_worker_message(self, worker_email: str) -> None:
        ...
