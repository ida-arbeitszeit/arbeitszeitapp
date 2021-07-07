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


class WorkerDoesNotExist(Exception):
    def __init__(self, worker: Member) -> None:
        self.worker = worker
        super().__init__()


class CompanyDoesNotExist(Exception):
    def __init__(self, company: Company) -> None:
        self.company = company
        super().__init__()


class CompanyIsNotPlanner(Exception):
    def __init__(self, company: Company, planner: Company) -> None:
        self.company = company
        self.planner = planner
        super().__init__()


class PlanDoesNotExist(Exception):
    def __init__(self, plan: Plan) -> None:
        self.plan = plan
        super().__init__()
