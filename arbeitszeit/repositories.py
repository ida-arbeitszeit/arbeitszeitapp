from abc import ABC, abstractmethod
from typing import List

from arbeitszeit.entities import Account, Company, Member, Plan, Purchase, Transaction


class CompanyWorkerRepository(ABC):
    @abstractmethod
    def add_worker_to_company(self, company: Company, worker: Member) -> None:
        pass

    @abstractmethod
    def get_company_workers(self, company: Company) -> List[Member]:
        pass


class PurchaseRepository(ABC):
    @abstractmethod
    def add(self, purchase: Purchase) -> None:
        pass


class PlanRepository(ABC):
    @abstractmethod
    def add(self, plan: Plan) -> None:
        pass


class TransactionRepository(ABC):
    @abstractmethod
    def add(self, transaction: Transaction) -> None:
        pass


class AccountRepository(ABC):
    @abstractmethod
    def add(self, account: Account) -> None:
        pass
