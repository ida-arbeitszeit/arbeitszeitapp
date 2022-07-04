from arbeitszeit.entities import Plan


class PlanIsInactive(Exception):
    def __init__(self, plan: Plan) -> None:
        self.plan = plan
        super().__init__()


class CannotSendEmail(Exception):
    pass
