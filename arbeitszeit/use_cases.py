from dataclasses import dataclass
from typing import Union, List
from decimal import Decimal
from enum import Enum
import datetime

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import (
    Company,
    Member,
    Plan,
    ProductOffer,
    Purchase,
    Account,
    SocialAccounting,
)
from arbeitszeit.errors import WorkerAlreadyAtCompany
from arbeitszeit.purchase_factory import PurchaseFactory
from arbeitszeit.transaction_factory import TransactionFactory
from arbeitszeit.repositories import (
    CompanyWorkerRepository,
    TransactionRepository,
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
            deactivate_offer(product_offer)

        return purchase


def deactivate_offer(product_offer: ProductOffer) -> ProductOffer:
    product_offer.deactivate()
    return product_offer


def adjust_balance(account: Account, amount: Decimal) -> Account:
    """changes the balance of specified accounts."""
    account.change_credit(amount)
    return account


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


def seek_approval(
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


def grant_credit(
    plan: Plan,
    social_accounting: SocialAccounting,
    transaction_repository: TransactionRepository,
    transaction_factory: TransactionFactory,
) -> None:
    """Social Accounting grants credit after plan has been approved."""
    assert plan.approved == True, "Plan has not been approved!"
    social_accounting_account = social_accounting.account

    prd = plan.costs_p + plan.costs_r + plan.costs_a
    accounts_and_amounts = [
        (plan.planner.means_account, plan.costs_p),
        (plan.planner.raw_material_account, plan.costs_r),
        (plan.planner.work_account, plan.costs_a),
        (plan.planner.product_account, -prd),
    ]

    for account, amount in accounts_and_amounts:
        adjust_balance(account, amount)
        transaction = transaction_factory.create_transaction(
            account_from=social_accounting_account,
            account_to=account,
            amount=amount,
            purpose=f"Plan-Id: {plan.id}",
        )
        transaction_repository.add(transaction)


def check_plans_for_expiration(plans: List[Plan]) -> List[Plan]:
    """
    checks if plans are expired and sets them as expired, if so.
    """

    for plan in plans:
        expiration_date = plan.plan_creation_date + datetime.timedelta(
            days=int(plan.timeframe)
        )
        expiration_relative = DatetimeService().now() - expiration_date
        seconds = expiration_relative.total_seconds()
        if seconds > 0:
            plan.set_as_expired()

    return plans
