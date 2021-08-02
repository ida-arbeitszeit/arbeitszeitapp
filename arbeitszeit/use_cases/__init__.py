import datetime
from dataclasses import dataclass
from typing import List, Optional, Union

from injector import inject

from arbeitszeit import errors
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import (
    Company,
    Member,
    Plan,
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

from .grant_credit import GrantCredit
from .pay_consumer_product import PayConsumerProduct
from .pay_means_of_production import PayMeansOfProduction
from .query_products import ProductFilter, QueryProducts
from .query_purchases import QueryPurchases
from .register_member import RegisterMember
from .seek_approval import SeekApproval
from .send_work_certificates_to_worker import SendWorkCertificatesToWorker

__all__ = [
    "GrantCredit",
    "PayConsumerProduct",
    "PayMeansOfProduction",
    "ProductFilter",
    "PurchaseProduct",
    "QueryProducts",
    "QueryPurchases",
    "RegisterMember",
    "SendWorkCertificatesToWorker",
    "add_worker_to_company",
    "check_plans_for_expiration",
    "deactivate_offer",
    "seek_approval",
]


@inject
@dataclass
class PurchaseProduct:
    datetime_service: DatetimeService
    purchase_factory: PurchaseFactory
    transaction_factory: TransactionFactory
    purchase_repository: PurchaseRepository
    transaction_repository: TransactionRepository

    def __call__(
        self,
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

        # create transaction
        price_total = purchase.price * purchase.amount

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
        self.purchase_repository.add(purchase)
        self.transaction_repository.add(transaction)

        # adjust balances of buyer and seller
        transaction.adjust_balances()


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
    company_workers = company_worker_repository.get_company_workers(company)
    if worker in company_workers:
        raise errors.WorkerAlreadyAtCompany(
            worker=worker,
            company=company,
        )
    company_worker_repository.add_worker_to_company(company, worker)


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


def calculate_plan_expiration(plan: Plan) -> Plan:
    """
    Based on a plan's creation date and timeframe this function
    calculates the plan's expiration date and days, hours, minutes
    missing until expiration.

    It stores these informations as attributes of the given Plan instance.
    """
    assert not plan.expired, "Plan is already expired"

    expiration_date = plan.plan_creation_date + datetime.timedelta(
        days=int(plan.timeframe)
    )
    expiration_relative = DatetimeService().now() - expiration_date
    seconds_until_exp = abs(expiration_relative.total_seconds())
    days = int(seconds_until_exp // 86400)
    seconds_until_exp = seconds_until_exp - (days * 86400)
    hours = int(seconds_until_exp // 3600)
    seconds_until_exp = seconds_until_exp - (hours * 3600)
    minutes = int(seconds_until_exp // 60)

    plan.expiration_relative = (days, hours, minutes)
    plan.expiration_date = expiration_date
    return plan
