from arbeitszeit import errors
from arbeitszeit.entities import Company, Member
from arbeitszeit.repositories import CompanyWorkerRepository

from .activate_plan_and_grant_credit import ActivatePlanAndGrantCredit
from .add_plan_to_cooperation import (
    AddPlanToCooperation,
    AddPlanToCooperationRequest,
    AddPlanToCooperationResponse,
)
from .answer_company_work_invite import (
    AnswerCompanyWorkInvite,
    AnswerCompanyWorkInviteRequest,
    AnswerCompanyWorkInviteResponse,
)
from .check_for_unread_messages import (
    CheckForUnreadMessages,
    CheckForUnreadMessagesRequest,
    CheckForUnreadMessagesResponse,
)
from .create_cooperation import (
    CreateCooperation,
    CreateCooperationRequest,
    CreateCooperationResponse,
)
from .create_plan_draft import (
    CreatePlanDraft,
    CreatePlanDraftRequest,
    CreatePlanDraftResponse,
)
from .delete_plan import DeletePlan, DeletePlanResponse
from .end_cooperation import (
    EndCooperation,
    EndCooperationRequest,
    EndCooperationResponse,
)
from .get_draft_summary import (
    DraftSummaryResponse,
    DraftSummarySuccess,
    GetDraftSummary,
)
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
from .list_drafts_of_company import ListDraftsOfCompany, ListDraftsResponse
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
from .query_purchases import PurchaseQueryResponse, QueryPurchases
from .read_message import (
    ReadMessage,
    ReadMessageFailure,
    ReadMessageRequest,
    ReadMessageResponse,
    ReadMessageSuccess,
)
from .register_company import RegisterCompany
from .register_member import RegisterMember
from .request_cooperation import (
    RequestCooperation,
    RequestCooperationRequest,
    RequestCooperationResponse,
)
from .seek_approval import SeekApproval
from .send_work_certificates_to_worker import SendWorkCertificatesToWorker
from .show_my_plans import ShowMyPlansRequest, ShowMyPlansResponse, ShowMyPlansUseCase
from .show_work_invites import ShowWorkInvites, ShowWorkInvitesRequest
from .toggle_product_availablity import (
    ToggleProductAvailability,
    ToggleProductAvailabilityResponse,
)
from .update_plans_and_payout import UpdatePlansAndPayout

__all__ = [
    "ActivatePlanAndGrantCredit",
    "AddPlanToCooperation",
    "AddPlanToCooperationRequest",
    "AddPlanToCooperationResponse",
    "AnswerCompanyWorkInvite",
    "AnswerCompanyWorkInviteRequest",
    "AnswerCompanyWorkInviteResponse",
    "CheckForUnreadMessages",
    "CheckForUnreadMessagesRequest",
    "CheckForUnreadMessagesResponse",
    "CompanyFilter",
    "CompanyQueryResponse",
    "CreateCooperation",
    "CreateCooperationRequest",
    "CreateCooperationResponse",
    "CreatePlanDraft",
    "CreatePlanDraftRequest",
    "CreatePlanDraftResponse",
    "DeletePlan",
    "DeletePlanResponse",
    "DraftQueryResponse",
    "DraftSummaryResponse",
    "DraftSummarySuccess",
    "EndCooperation",
    "EndCooperationResponse",
    "EndCooperationRequest",
    "GetMemberProfileInfo",
    "GetMemberProfileInfoResponse",
    "GetDraftSummary",
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
    "PurchaseQueryResponse",
    "QueryCompanies",
    "QueryCompaniesRequest",
    "QueryPlans",
    "QueryPlansRequest",
    "QueryPurchases",
    "RequestCooperation",
    "RequestCooperationRequest",
    "RequestCooperationResponse",
    "ListDraftsResponse",
    "ListDraftsOfCompany",
    "ReadMessage",
    "ReadMessageFailure",
    "ReadMessageRequest",
    "ReadMessageResponse",
    "ReadMessageSuccess",
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
    "ToggleProductAvailability",
    "ToggleProductAvailabilityResponse",
    "TransactionInfo",
    "UpdatePlansAndPayout",
    "UpdatePlansAndPayout",
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
