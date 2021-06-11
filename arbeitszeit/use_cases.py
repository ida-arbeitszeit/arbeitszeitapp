from dataclasses import dataclass
from typing import Union
from decimal import Decimal
from enum import Enum

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import (
    Company,
    Member,
    Plan,
    ProductOffer,
    Purchase,
    Account,
    Transaction,
)
from arbeitszeit.errors import WorkerAlreadyAtCompany
from arbeitszeit.purchase_factory import PurchaseFactory
from arbeitszeit.repositories import (
    CompanyWorkerRepository,
)


class PurposesOfPurchases(Enum):
    means_of_prod = "means_of_prod"
    raw_materials = "raw_materials"
    consumption = "consumption"


@inject
@dataclass
class PurchaseProduct:
    datetime_service: DatetimeService
    purchase_factory: PurchaseFactory

    def __call__(
        self,
        product_offer: ProductOffer,
        amount: int,
        purpose: PurposesOfPurchases,
        buyer: Union[Member, Company],
    ) -> Purchase:
        price = product_offer.price_per_unit
        purchase = self.purchase_factory.create_private_purchase(
            purchase_date=self.datetime_service.now(),
            product_offer=product_offer,
            buyer=buyer,
            price=price,
            amount=amount,
            purpose=purpose,
        )
        assert (
            product_offer.amount_available >= amount
        ), "Amount ordered exceeds available products!"
        product_offer.decrease_amount_available(amount)
        if product_offer.amount_available == 0:
            product_offer.deactivate()

        return purchase


def adjust_balance(account: Account, amount: Decimal) -> Account:
    """changes the balance of specified accounts."""
    account.change_credit(amount)
    return account


def register_transaction(
    account_from: Account,
    account_to: Account,
    amount: Decimal,
    purpose: str,
) -> Transaction:
    transaction = Transaction(account_from, account_to, amount, purpose)
    return transaction


def add_worker_to_company(
    company_worker_repository: CompanyWorkerRepository,
    company: Company,
    worker: Member,
) -> None:
    """This function may raise a WorkerAlreadyAtCompany exception if the
    worker is already employed at the company."""
    company_workers = company_worker_repository.get_company_workers(company)
    if worker in company_workers:
        raise WorkerAlreadyAtCompany(
            worker=worker,
            company=company,
        )
    company_worker_repository.add_worker_to_company(company, worker)


def approve_plan(
    datetime_service: DatetimeService,
    plan: Plan,
) -> Plan:
    """Company seeks plan approval from Social Accounting."""
    # This is just a place holder
    is_approval = True
    approval_date = datetime_service.now()
    if is_approval:
        plan.approve(approval_date)
    else:
        plan.deny("Some reason", approval_date)
    return plan
