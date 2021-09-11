from arbeitszeit import errors
from arbeitszeit.entities import Company, Member, ProductOffer
from arbeitszeit.repositories import CompanyWorkerRepository

from .calculate_plan_expiration import CalculatePlanExpirationAndCheckIfExpired
from .create_offer import CreateOffer, CreateOfferRequest, CreateOfferResponse
from .create_production_plan import CreatePlan, PlanProposal
from .delete_plan import DeletePlan, DeletePlanResponse
from .get_member_profile_info import GetMemberProfileInfo, MemberProfileInfo, Workplace
from .get_plan_summary import GetPlanSummary
from .get_statistics import GetStatistics, StatisticsResponse
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
    "CreateOfferResponse",
    "CreateOfferRequest",
    "CreatePlan",
    "DeletePlan",
    "DeletePlanResponse",
    "GetMemberProfileInfo",
    "GetPlanSummary",
    "GetStatistics",
    "GetTransactionInfos",
    "MemberProfileInfo",
    "PayConsumerProduct",
    "PayMeansOfProduction",
    "PlanProposal",
    "ProductFilter",
    "ProductQueryResponse",
    "PurchaseQueryResponse",
    "QueryProducts",
    "QueryPurchases",
    "RegisterCompany",
    "RegisterMember",
    "SeekApproval",
    "SendWorkCertificatesToWorker",
    "StatisticsResponse",
    "SynchronizedPlanActivation",
    "TransactionInfo",
    "Workplace",
    "add_worker_to_company",
    "deactivate_offer",
]


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
