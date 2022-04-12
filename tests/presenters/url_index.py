from uuid import UUID


class ListMessageUrlIndexTestImpl:
    def get_list_messages_url(self) -> str:
        return "list messages"


class PlanSummaryUrlIndexTestImpl:
    def get_plan_summary_url(self, plan_id: UUID) -> str:
        return f"fake_plan_url:{plan_id}"


class CoopSummaryUrlIndexTestImpl:
    def get_coop_summary_url(self, coop_id: UUID) -> str:
        return f"fake_coop_url:{coop_id}"


class EndCoopUrlIndexTestImpl:
    def get_end_coop_url(self, plan_id: UUID, cooperation_id: UUID) -> str:
        return f"fake_end_coop_url:{plan_id}, {cooperation_id}"
