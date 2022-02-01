from uuid import UUID

from flask import url_for


class MemberUrlIndex:
    def get_plan_summary_url(self, plan_id: UUID) -> str:
        return url_for("main_member.plan_summary", plan_id=plan_id)

    def get_message_url(self, message_id: UUID) -> str:
        return url_for("main_member.read_message", message_id=message_id)

    def get_coop_summary_url(self, coop_id: UUID) -> str:
        return url_for("main_member.coop_summary", coop_id=coop_id)

    def get_toggle_availability_url(self, plan_id: UUID) -> str:
        ...

    def get_renew_plan_url(self, plan_id: UUID) -> str:
        ...

    def get_hide_plan_url(self, plan_id: UUID) -> str:
        ...

    def get_end_coop_url(self, plan_id: UUID, cooperation_id: UUID) -> str:
        ...

    def get_confirmation_url(self, token: str) -> str:
        return url_for(
            endpoint="auth.confirm_email_member", token=token, _external=True
        )


class CompanyUrlIndex:
    def get_plan_summary_url(self, plan_id: UUID) -> str:
        return url_for("main_company.plan_summary", plan_id=plan_id)

    def get_message_url(self, message_id: UUID) -> str:
        return url_for("main_company.read_message", message_id=message_id)

    def get_coop_summary_url(self, coop_id: UUID) -> str:
        return url_for("main_company.coop_summary", coop_id=coop_id)

    def get_toggle_availability_url(self, plan_id: UUID) -> str:
        return url_for("main_company.toggle_availability", plan_id=plan_id)

    def get_renew_plan_url(self, plan_id: UUID) -> str:
        return url_for(
            "main_company.create_draft_from_expired_plan", expired_plan_id=plan_id
        )

    def get_hide_plan_url(self, plan_id: UUID) -> str:
        return url_for("main_company.hide_plan", plan_id=plan_id)

    def get_end_coop_url(self, plan_id: UUID, cooperation_id: UUID) -> str:
        return url_for(
            "main_company.end_cooperation",
            plan_id=plan_id,
            cooperation_id=cooperation_id,
        )

    def get_confirmation_url(self, token: str) -> str:
        return url_for(
            endpoint="auth.confirm_email_company", token=token, _external=True
        )
