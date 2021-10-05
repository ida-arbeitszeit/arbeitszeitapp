from arbeitszeit import errors
from arbeitszeit.entities import Company, Member
from arbeitszeit.repositories import CompanyWorkerRepository

from .calculate_plan_expiration import CalculatePlanExpirationAndCheckIfExpired
from .create_offer import CreateOffer, CreateOfferRequest, CreateOfferResponse
from .create_plan_draft import CreatePlanDraft, CreatePlanDraftRequest
from .delete_offer import DeleteOffer, DeleteOfferRequest, DeleteOfferResponse
from .delete_plan import DeletePlan, DeletePlanResponse
from .get_member_profile_info import (
    GetMemberProfileInfo,
    GetMemberProfileInfoResponse,
    Workplace,
)
from .get_plan_summary import GetPlanSummary
from .get_statistics import GetStatistics, StatisticsResponse
from .get_transaction_infos import GetTransactionInfos, TransactionInfo
from .pay_consumer_product import (
    PayConsumerProduct,
    PayConsumerProductRequest,
    PayConsumerProductResponse,
)
from .pay_means_of_production import PayMeansOfProduction, PayMeansOfProductionRequest
from .query_products import (
    ProductFilter,
    ProductQueryResponse,
    QueryProducts,
    QueryProductsRequest,
)
from .query_purchases import PurchaseQueryResponse, QueryPurchases
from .register_company import RegisterCompany
from .register_member import RegisterMember
from .seek_approval import SeekApproval
from .send_work_certificates_to_worker import SendWorkCertificatesToWorker
from .show_my_plans import ShowMyPlansRequest, ShowMyPlansResponse, ShowMyPlansUseCase
from .synchronized_plan_activation import SynchronizedPlanActivation

__all__ = [
    "CalculatePlanExpirationAndCheckIfExpired",
    "CreateOffer",
    "CreateOfferRequest",
    "CreateOfferResponse",
    "CreatePlanDraft",
    "DeleteOffer",
    "DeleteOfferRequest",
    "DeleteOfferResponse",
    "DeletePlan",
    "DeletePlanResponse",
    "GetMemberProfileInfo",
    "GetMemberProfileInfoResponse",
    "GetPlanSummary",
    "GetStatistics",
    "GetTransactionInfos",
    "PayConsumerProduct",
    "PayConsumerProductRequest",
    "PayConsumerProductResponse",
    "PayMeansOfProduction",
    "PayMeansOfProductionRequest",
    "PlanProposal",
    "CreatePlanDraftRequest",
    "CreatePlanDraftResponse",
    "ProductFilter",
    "ProductQueryResponse",
    "PurchaseQueryResponse",
    "QueryProducts",
    "QueryProductsRequest",
    "QueryPurchases",
    "RegisterCompany",
    "RegisterMember",
    "SeekApproval",
    "SendWorkCertificatesToWorker",
    "ShowMyPlansRequest",
    "ShowMyPlansResponse",
    "ShowMyPlansUseCase",
    "StatisticsResponse",
    "SynchronizedPlanActivation",
    "TransactionInfo",
    "Workplace",
    "add_worker_to_company",
]


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
