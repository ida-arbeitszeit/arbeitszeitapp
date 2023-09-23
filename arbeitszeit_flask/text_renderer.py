from flask import render_template


class TextRendererImpl:
    def render_member_registration_message(self, *, confirmation_url: str) -> str:
        return render_template(
            "auth/activate.html",
            confirm_url=confirmation_url,
        )

    def render_company_registration_message(self, *, confirmation_url: str) -> str:
        return render_template(
            "auth/activate.html",
            confirm_url=confirmation_url,
        )

    def render_accountant_notification_about_new_plan(
        self, *, product_name: str, accountant_name: str
    ) -> str:
        return render_template(
            "accountant/notification-about-new-plan.html",
            product_name=product_name,
            accountant_name=accountant_name,
        )

    def render_member_notfication_about_work_invitation(
        self, *, invitation_url: str
    ) -> str:
        return render_template(
            "member/notification-about-work-invitation.html",
            invitation_url=invitation_url,
        )
