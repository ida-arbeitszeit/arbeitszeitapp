from dataclasses import dataclass

from flask import render_template

from arbeitszeit_flask.mail_service import MailService
from arbeitszeit_flask.template import TemplateRenderer
from arbeitszeit_web.www.presenters.accountant_invitation_presenter import ViewModel


@dataclass
class AccountantInvitationEmailViewImpl:
    mail_service: MailService
    template_renderer: TemplateRenderer

    def render_accountant_invitation_email(self, view_model: ViewModel) -> None:
        html = render_template(
            "auth/accountant_invitation.html",
            view_model=view_model,
        )
        self.mail_service.send_message(
            subject=view_model.subject,
            recipients=view_model.recipients,
            html=html,
            sender=view_model.sender,
        )
