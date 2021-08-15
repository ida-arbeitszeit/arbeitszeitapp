from arbeitszeit.entities import Company, Member, Plan


class WorkerAlreadyAtCompany(Exception):
    def __init__(self, worker: Member, company: Company) -> None:
        self.worker = worker
        self.company = company
        super().__init__()


class WorkerNotAtCompany(Exception):
    def __init__(self, worker: Member, company: Company) -> None:
        self.worker = worker
        self.company = company
        super().__init__()


class CompanyIsNotPlanner(Exception):
    def __init__(self, company: Company, planner: Company) -> None:
        self.company = company
        self.planner = planner
        super().__init__()


class PlanIsExpired(Exception):
    def __init__(self, plan: Plan) -> None:
        self.plan = plan
        super().__init__()


class MemberAlreadyExists(Exception):
    pass


class CompanyAlreadyExists(Exception):
    pass


class CompanyCantBuyPublicServices(Exception):
    def __init__(self, company: Company, plan: Plan) -> None:
        self.company = company
        self.plan = plan
        super().__init__()
