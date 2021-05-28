from arbeitszeit.entities import Company, Member


class WorkerAlreadyAtCompany(Exception):
    def __init__(self, worker: Member, company: Company) -> None:
        self.worker = worker
        self.company = company
        super().__init__()
