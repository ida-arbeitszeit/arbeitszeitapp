from dataclasses import dataclass

from arbeitszeit import email_notifications as interface
from arbeitszeit_web.email.email_change_warning_view import EmailChangeWarningView
from arbeitszeit_web.email.notify_worker_about_removal_from_company_presenter import (
    NotifyWorkerAboutRemovalPresenter,
)
from arbeitszeit_web.email.request_coordination_transfer_presenter import (
    RequestCoordinationTransferEmailPresenter,
)

from .accountant_invitation_presenter import AccountantInvitationEmailPresenter
from .company_notifier import CompanyNotifier
from .cooperation_request_email_presenter import CooperationRequestEmailPresenter
from .email_change_confirmation_presenter import EmailChangeConfirmationPresenter
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
    notify_worker_about_removal_presenter: NotifyWorkerAboutRemovalPresenter
    request_cooperation_presenter: CooperationRequestEmailPresenter
    email_change_confirmation_presenter: EmailChangeConfirmationPresenter
    email_change_warning_view: EmailChangeWarningView
    request_coordination_transfer_email_presenter: (
        RequestCoordinationTransferEmailPresenter
    )
    company_notifier: CompanyNotifier

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
        elif isinstance(message, interface.WorkerRemovalNotification):
            self.notify_worker_about_removal_presenter.notify(
                message.worker_email, message.company_name
            )
        elif isinstance(message, interface.CooperationRequestEmail):
            self.request_cooperation_presenter.present(message)
        elif isinstance(message, interface.EmailChangeWarning):
            self.email_change_warning_view.render_email_change_warning(message)
        elif isinstance(message, interface.EmailChangeConfirmation):
            self.email_change_confirmation_presenter.present_email_change_confirmation(
                message
            )
        elif isinstance(message, interface.CoordinationTransferRequest):
            self.request_coordination_transfer_email_presenter.present(message)
        elif isinstance(message, interface.RejectedPlanNotification):
            self.company_notifier.notify_planning_company_about_rejected_plan(message)

        else:
            raise NotImplementedError()
