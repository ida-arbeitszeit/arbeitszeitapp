from dataclasses import dataclass
from typing import Union

from injector import inject

from arbeitszeit import errors
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Company, Member, ProductOffer, PurposesOfPurchases
from arbeitszeit.purchase_factory import PurchaseFactory
from arbeitszeit.repositories import (
    CompanyWorkerRepository,
    PurchaseRepository,
    TransactionRepository,
)

from .calculate_plan_expiration import CalculatePlanExpirationAndCheckIfExpired
from .create_offer import CreateOffer, Offer
from .create_production_plan import CreatePlan, PlanProposal
from .get_plan_summary import GetPlanSummary
from .get_transaction_infos import GetTransactionInfos, TransactionInfo
from .pay_consumer_product import PayConsumerProduct
from .pay_means_of_production import PayMeansOfProduction
from .query_products import ProductFilter, ProductQueryResponse, QueryProducts
from .query_purchases import PurchaseQueryResponse, QueryPurchases
from .register_company import RegisterCompany
from .register_member import RegisterMember
from .seek_approval import SeekApproval
from .send_work_certificates_to_worker import SendWorkCertificatesToWorker
from .synchronized_plan_activation import SynchronizedPlanActivation

__all__ = [
    "CalculatePlanExpirationAndCheckIfExpired",
    "CreateOffer",
    "CreatePlan",
    "GetPlanSummary",
    "GetTransactionInfos",
    "Offer",
    "PayConsumerProduct",
    "PayMeansOfProduction",
    "PlanProposal",
    "ProductFilter",
    "ProductQueryResponse",
    "PurchaseProduct",
    "PurchaseQueryResponse",
    "QueryProducts",
    "QueryPurchases",
    "RegisterCompany",
    "RegisterMember",
    "SeekApproval",
    "SendWorkCertificatesToWorker",
    "SynchronizedPlanActivation",
    "TransactionInfo",
    "add_worker_to_company",
    "deactivate_offer",
]


@inject
@dataclass
class PurchaseProduct:
    datetime_service: DatetimeService
    purchase_factory: PurchaseFactory
    purchase_repository: PurchaseRepository
    transaction_repository: TransactionRepository

    def __call__(
        self,
        product_offer: ProductOffer,
        amount: int,
        purpose: PurposesOfPurchases,
        buyer: Union[Member, Company],
    ) -> None:

        if isinstance(buyer, Company) and product_offer.plan.is_public_service:
            raise errors.CompanyCantBuyPublicServices(buyer, product_offer.plan)

        assert (
            product_offer.amount_available >= amount
        ), "Amount ordered exceeds available products!"

        # create purchase
        price_per_unit = product_offer.price_per_unit()
        purchase = self.purchase_factory.create_private_purchase(
            purchase_date=self.datetime_service.now(),
            product_offer=product_offer,
            buyer=buyer,
            price_per_unit=price_per_unit,
            amount=amount,
            purpose=purpose,
        )

        # decrease amount available
        product_offer.decrease_amount_available(amount)

        # deactivate offer if amount is zero
        if product_offer.amount_available == 0:
            deactivate_offer(product_offer)

        # create transaction
        price_total = purchase.price_per_unit * purchase.amount

        if isinstance(buyer, Member):
            account_from = buyer.account
        else:
            if purpose.value == "means_of_prod":
                account_from = buyer.means_account
            else:
                account_from = buyer.raw_material_account

        send_to = product_offer.plan.planner.product_account
        self.transaction_repository.create_transaction(
            date=self.datetime_service.now(),
            account_from=account_from,
            account_to=send_to,
            amount=price_total,
            purpose=f"Angebot-Id: {product_offer.id}",
        )
        self.purchase_repository.add(purchase)


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
