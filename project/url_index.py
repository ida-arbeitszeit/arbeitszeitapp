from uuid import UUID

from flask import url_for


class MemberUrlIndex:
    def get_plan_summary_url(self, plan_id: UUID) -> str:
        return url_for("main_member.plan_summary", plan_id=plan_id)


class CompanyUrlIndex:
    def get_plan_summary_url(self, plan_id: UUID) -> str:
        return url_for("main_company.plan_summary", plan_id=plan_id)
