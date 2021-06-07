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
        assert (
            product_offer.amount_available >= amount
        ), "Amount ordered exceeds available products!"
        product_offer.decrease_amount_available(amount)
        if product_offer.amount_available == amount:
            product_offer.deactivate()
        price_total = price * amount
        product_offer.provider.increase_credit(price_total, "balance_prd")
        account_type = "balance_p" if purpose == "means_of_prod" else "balance_r"
        if isinstance(buyer, Member):
            buyer.reduce_credit(price_total)
        else:
            buyer.reduce_credit(price_total, account_type)
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
    # This is just a place holder
    is_approval = True
    approval_date = datetime_service.now()
    if is_approval:
        plan.approve(approval_date)
    else:
        plan.deny("Some reason", approval_date)
    return plan


def granting_credit(
    plan: Plan,
) -> None:
    # increase/reduce company balances
    # register transcations
    pass
