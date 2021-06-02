from dataclasses import dataclass
from typing import Union

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Company, Member, Plan, ProductOffer, Purchase
from arbeitszeit.errors import WorkerAlreadyAtCompany
from arbeitszeit.purchase_factory import PurchaseFactory
from arbeitszeit.repositories import CompanyWorkerRepository, PurchaseRepository


@inject
@dataclass
class PurchaseProduct:
    purchase_repository: PurchaseRepository
    datetime_service: DatetimeService
    purchase_factory: PurchaseFactory

    def __call__(
        self,
        product_offer: ProductOffer,
        amount: int,
        purpose: str,
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
        product_offer.decrease_amount_available(amount)
        assert (
            product_offer.amount_available >= amount
        ), "Amount ordered exceeds available products!"
        if product_offer.amount_available == amount:
            product_offer.deactivate()

        product_offer.provider.increase_credit(price * amount, "balance_prd")
        account_type = "balance_p" if purpose == "means_of_prod" else "balance_r"
        buyer.reduce_credit(price * amount, account_type)
        self.purchase_repository.add(purchase)
        return purchase


def add_worker_to_company(
    company_worker_repository: CompanyWorkerRepository,
    company: Company,
    worker: Member,
) -> None:
    """This function may raise a WorkerAlreadyAtCompany exception if the
    worker is already employed at the company."""
    company_workers = company_worker_repository.get_company_workers(company)
    if worker.id in [worker.id for worker in company_workers]:
        raise WorkerAlreadyAtCompany(
            worker=worker,
            company=company,
        )
    company_worker_repository.add_worker_to_company(company, worker)


def seeking_approval(
    datetime_service: DatetimeService,
    plan: Plan,
) -> Plan:
    # criteria to be defined
    decision = True
    reason = None if decision else "Nicht genug Kredit."
    approval_date = datetime_service.now() if decision else None

    plan.approve(decision, reason, approval_date)
    return plan


def granting_credit(
    plan: Plan,
) -> None:
    # increase/reduce company balances
    # register transcations
    return plan
