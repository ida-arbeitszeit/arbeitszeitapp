import datetime
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional, Union

from injector import inject

from arbeitszeit import errors
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import (
    Company,
    Member,
    Plan,
    PlanRenewal,
    ProductOffer,
    PurposesOfPurchases,
)
from arbeitszeit.purchase_factory import PurchaseFactory
from arbeitszeit.repositories import (
    CompanyWorkerRepository,
    PurchaseRepository,
    TransactionRepository,
)
from arbeitszeit.transaction_factory import TransactionFactory

# do not delete
from .adjust_balance import adjust_balance
from .grant_credit import GrantCredit
from .query_products import ProductFilter, QueryProducts
from .send_work_certificates_to_worker import SendWorkCertificatesToWorker


@inject
@dataclass
class PurchaseProduct:
    datetime_service: DatetimeService
    purchase_factory: PurchaseFactory
    transaction_factory: TransactionFactory

    def __call__(
        self,
        purchase_repository: PurchaseRepository,
        transaction_repository: TransactionRepository,
        product_offer: ProductOffer,
        amount: int,
        purpose: PurposesOfPurchases,
        buyer: Union[Member, Company],
    ) -> None:

        assert (
            product_offer.amount_available >= amount
        ), "Amount ordered exceeds available products!"

        # create purchase
        price = product_offer.price_per_unit
        purchase = self.purchase_factory.create_private_purchase(
            purchase_date=self.datetime_service.now(),
            product_offer=product_offer,
            buyer=buyer,
            price=price,
            amount=amount,
            purpose=purpose,
        )

        # decrease amount available
        product_offer.decrease_amount_available(amount)

        # deactivate offer if amount is zero
        if product_offer.amount_available == 0:
            deactivate_offer(product_offer)

        # reduce balance of buyer
        price_total = purchase.price * purchase.amount
        if isinstance(buyer, Member):
            adjust_balance(
                buyer.account,
                -price_total,
            )
        else:
            if purpose.value == "means_of_prod":
                adjust_balance(
                    buyer.means_account,
                    -price_total,
                )
            else:
                adjust_balance(
                    buyer.raw_material_account,
                    -price_total,
                )

        # increase balance of seller
        adjust_balance(product_offer.provider.product_account, price_total)

        # create transaction
        if isinstance(buyer, Member):
            account_from = buyer.account
        else:
            if purpose.value == "means_of_prod":
                account_from = buyer.means_account
            else:
                account_from = buyer.raw_material_account

        send_to = product_offer.provider.product_account

        transaction = self.transaction_factory.create_transaction(
            account_from=account_from,
            account_to=send_to,
            amount=price_total,
            purpose=f"Angebot-Id: {product_offer.id}",
        )

        # add purchase and transaction to database
        purchase_repository.add(purchase)
        transaction_repository.add(transaction)


def deactivate_offer(product_offer: ProductOffer) -> ProductOffer:
    product_offer.deactivate()
    return product_offer


def add_worker_to_company(
    company_worker_repository: CompanyWorkerRepository,
    company: Company,
    worker: Member,
) -> None:
    """This function may raise a WorkerAlreadyAtCompany exception if the
    worker is already employed at the company."""
    if not company:
        raise errors.CompanyDoesNotExist(company=company)
    if not worker:
        raise errors.WorkerDoesNotExist(
            worker=worker,
        )
    company_workers = company_worker_repository.get_company_workers(company)
    if worker in company_workers:
        raise errors.WorkerAlreadyAtCompany(
            worker=worker,
            company=company,
        )
    company_worker_repository.add_worker_to_company(company, worker)


def seek_approval(
    datetime_service: DatetimeService,
    plan: Plan,
    plan_renewal: Optional[PlanRenewal],
) -> Plan:
    """
    Company seeks plan approval.
    It can be a new plan or a plan renewal, in which case the original plan will be set as "renewed".
    """
    # This is just a place holder
    is_approval = True
    approval_date = datetime_service.now()
    if is_approval:
        plan.approve(approval_date)
        if plan_renewal:
            plan_renewal.original_plan.set_as_renewed()
    else:
        plan.deny("Some reason", approval_date)
    return plan


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


def pay_means_of_production(
    transaction_repository: TransactionRepository,
    sender: Company,
    receiver: Company,
    plan: Plan,
    amount: int,
    purpose: PurposesOfPurchases,
) -> None:
    """payment of means of production or raw materials which were not offered/bought on the app's marketplace."""
    if not receiver:
        raise errors.CompanyDoesNotExist(
            company=receiver,
        )
    if not plan:
        raise errors.PlanDoesNotExist(
            plan=plan,
        )
    if plan.planner != receiver:
        raise errors.CompanyIsNotPlanner(
            company=receiver,
            planner=plan.planner,
        )
    # no purchase!

    # reduce balance of buyer
    price_total = amount * (plan.costs_p + plan.costs_r + plan.costs_a)
    if purpose == "means_of_prod":
        adjust_balance(
            sender.means_account,
            -price_total,
        )
    elif purpose == "raw_materials":
        adjust_balance(
            sender.raw_material_account,
            -price_total,
        )

    # increase balance of seller
    adjust_balance(plan.planner.product_account, price_total)

    # create transaction
    if purpose == "means_of_prod":
        account_from = sender.means_account
    elif purpose == "raw_materials":
        account_from = sender.raw_material_account

    transaction_factory = TransactionFactory()
    transaction = transaction_factory.create_transaction(
        account_from=account_from,
        account_to=plan.planner.product_account,
        amount=price_total,
        purpose=f"Plan-Id: {plan.id}",
    )

    # add transaction to database
    transaction_repository.add(transaction)
