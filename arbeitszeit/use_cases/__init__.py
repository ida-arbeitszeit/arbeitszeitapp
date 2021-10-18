from arbeitszeit import errors
from arbeitszeit.entities import Company, Member
from arbeitszeit.repositories import CompanyWorkerRepository

from .activate_plan_and_grant_credit import ActivatePlanAndGrantCredit
from .answer_company_work_invite import (
    AnswerCompanyWorkInvite,
    AnswerCompanyWorkInviteRequest,
    AnswerCompanyWorkInviteResponse,
)
from .create_offer import CreateOffer, CreateOfferRequest, CreateOfferResponse
from .create_plan_draft import (
    CreatePlanDraft,
    CreatePlanDraftRequest,
    CreatePlanDraftResponse,
)
from .delete_offer import DeleteOffer, DeleteOfferRequest, DeleteOfferResponse
from .delete_plan import DeletePlan, DeletePlanResponse
from .get_member_profile_info import (
    GetMemberProfileInfo,
    GetMemberProfileInfoResponse,
    Workplace,
)
from .get_plan_summary import GetPlanSummary, PlanSummaryResponse, PlanSummarySuccess
from .get_statistics import GetStatistics, StatisticsResponse
from .get_transaction_infos import GetTransactionInfos, TransactionInfo
from .invite_worker_to_company import (
    InviteWorkerToCompany,
    InviteWorkerToCompanyRequest,
)
from .pay_consumer_product import (
    PayConsumerProduct,
    PayConsumerProductRequest,
    PayConsumerProductResponse,
)
from .pay_means_of_production import PayMeansOfProduction, PayMeansOfProductionRequest
from .query_companies import (
    CompanyFilter,
    CompanyQueryResponse,
    QueryCompanies,
    QueryCompaniesRequest,
)
from .query_plans import PlanFilter, PlanQueryResponse, QueryPlans, QueryPlansRequest
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
from .show_work_invites import ShowWorkInvites, ShowWorkInvitesRequest
from .update_plans_and_payout import UpdatePlansAndPayout

__all__ = [
    "ActivatePlanAndGrantCredit",
    "AnswerCompanyWorkInvite",
    "AnswerCompanyWorkInviteRequest",
    "AnswerCompanyWorkInviteResponse",
    "CompanyFilter",
    "CompanyQueryResponse",
    "CreateOffer",
    "CreateOfferRequest",
    "CreateOfferResponse",
    "CreatePlanDraft",
    "CreatePlanDraftRequest",
    "CreatePlanDraftRequest",
    "CreatePlanDraftResponse",
    "CreatePlanDraftResponse",
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
    "InviteWorkerToCompany",
    "InviteWorkerToCompanyRequest",
    "PayConsumerProduct",
    "PayConsumerProductRequest",
    "PayConsumerProductResponse",
    "PayMeansOfProduction",
    "PayMeansOfProductionRequest",
    "PlanFilter",
    "PlanQueryResponse",
    "PlanSummaryResponse",
    "PlanSummarySuccess",
    "ProductFilter",
    "ProductQueryResponse",
    "PurchaseQueryResponse",
    "QueryCompanies",
    "QueryCompaniesRequest",
    "QueryPlans",
    "QueryPlansRequest",
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
    "ShowWorkInvites",
    "ShowWorkInvitesRequest",
    "StatisticsResponse",
    "TransactionInfo",
    "UpdatePlansAndPayout",
    "Workplace",
    "add_worker_to_company",
    "UpdatePlansAndPayout",
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
