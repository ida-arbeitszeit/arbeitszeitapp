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

    def render_email_change_warning(self, *, admin_email_address: str | None) -> str:
        return render_template(
            "user/request_email_change_warning.html",
            admin_email_address=admin_email_address,
        )

    def render_email_change_notification(self, *, change_email_url: str) -> str:
        return render_template(
            "user/request_email_change_notification.html",
            change_email_url=change_email_url,
        )

    def render_company_notification_about_rejected_plan(
        self, company_name: str, product_name: str, plan_id: str
    ) -> str:
        return render_template(
            "company/rejected_plan_notification.html",
            product_name=product_name,
            plan_id=plan_id,
            company_name=company_name,
        )
