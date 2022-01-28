from uuid import UUID

from flask import url_for


class MemberUrlIndex:
    def get_plan_summary_url(self, plan_id: UUID) -> str:
        return url_for("main_member.plan_summary", plan_id=plan_id)

    def get_message_url(self, message_id: UUID) -> str:
        return url_for("main_member.read_message", message_id=message_id)

    def get_coop_summary_url(self, coop_id: UUID) -> str:
        return url_for("main_member.coop_summary", coop_id=coop_id)

    def get_invite_url(self, invite_id: UUID) -> str:
        raise Exception()

    def get_answer_company_work_invite_url(self, invite_id: UUID) -> str:
        return ""


class CompanyUrlIndex:
    def get_plan_summary_url(self, plan_id: UUID) -> str:
        return url_for("main_company.plan_summary", plan_id=plan_id)

    def get_message_url(self, message_id: UUID) -> str:
        return url_for("main_company.read_message", message_id=message_id)

    def get_coop_summary_url(self, coop_id: UUID) -> str:
        return url_for("main_company.coop_summary", coop_id=coop_id)

    def get_invite_url(self, invite_id: UUID) -> str:
        raise Exception()
