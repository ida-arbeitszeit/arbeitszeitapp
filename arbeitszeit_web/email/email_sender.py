from dataclasses import dataclass

from arbeitszeit import email_notifications as interface

from .accountant_invitation_presenter import AccountantInvitationEmailPresenter
from .invite_worker_presenter import InviteWorkerPresenterImpl
from .notify_accountant_about_new_plan_presenter import (
    NotifyAccountantsAboutNewPlanPresenterImpl,
)
from .registration_email_presenter import RegistrationEmailPresenter


@dataclass
class EmailSender:
    registration_email_presenter: RegistrationEmailPresenter
    notify_accountants_about_new_plan: NotifyAccountantsAboutNewPlanPresenterImpl
    accountant_invitation_presenter: AccountantInvitationEmailPresenter
    invite_worker_presenter: InviteWorkerPresenterImpl

    def send_email(self, message: interface.Message) -> None:
        if isinstance(message, interface.MemberRegistration):
            self.registration_email_presenter.show_member_registration_message(
                message.email_address
            )
        elif isinstance(message, interface.CompanyRegistration):
            self.registration_email_presenter.show_company_registration_message(
                message.email_address
            )
        elif isinstance(message, interface.AccountantNotificationAboutNewPlan):
            self.notify_accountants_about_new_plan.notify_accountant_about_new_plan(
                message
            )
        elif isinstance(message, interface.AccountantInvitation):
            self.accountant_invitation_presenter.send_accountant_invitation(
                message.email_address
            )
        elif isinstance(message, interface.WorkerInvitation):
            self.invite_worker_presenter.show_invite_worker_message(
                worker_email=message.worker_email,
                invite=message.invite,
            )
        elif isinstance(message, interface.EmailChangeConfirmation):
            raise NotImplementedError()
