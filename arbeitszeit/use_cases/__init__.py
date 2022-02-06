from arbeitszeit import errors
from arbeitszeit.entities import Company, Member
from arbeitszeit.repositories import CompanyWorkerRepository

from .accept_cooperation import (
    AcceptCooperation,
    AcceptCooperationRequest,
    AcceptCooperationResponse,
)
from .activate_plan_and_grant_credit import ActivatePlanAndGrantCredit
from .answer_company_work_invite import (
    AnswerCompanyWorkInvite,
    AnswerCompanyWorkInviteRequest,
    AnswerCompanyWorkInviteResponse,
)
from .cancel_cooperation_solicitation import (
    CancelCooperationSolicitation,
    CancelCooperationSolicitationRequest,
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
from .deny_cooperation import (
    DenyCooperation,
    DenyCooperationRequest,
    DenyCooperationResponse,
)
from .end_cooperation import (
    EndCooperation,
    EndCooperationRequest,
    EndCooperationResponse,
)
from .get_company_summary import (
    GetCompanySummary,
    GetCompanySummaryResponse,
    GetCompanySummarySuccess,
)
from .get_company_transactions import GetCompanyTransactions
from .get_coop_summary import (
    GetCoopSummary,
    GetCoopSummaryRequest,
    GetCoopSummaryResponse,
    GetCoopSummarySuccess,
)
from .get_draft_summary import (
    DraftSummaryResponse,
    DraftSummarySuccess,
    GetDraftSummary,
)
from .get_member_account import GetMemberAccount, GetMemberAccountResponse
from .get_member_profile_info import (
    GetMemberProfileInfo,
    GetMemberProfileInfoResponse,
    Workplace,
)
from .get_plan_summary import GetPlanSummary, PlanSummaryResponse, PlanSummarySuccess
from .get_statistics import GetStatistics, StatisticsResponse
from .hide_plan import HidePlan, HidePlanResponse
from .invite_worker_to_company import (
    InviteWorkerToCompany,
    InviteWorkerToCompanyRequest,
)
from .list_all_cooperations import (
    ListAllCooperations,
    ListAllCooperationsResponse,
    ListedCooperation,
)
from .list_coordinations import (
    CooperationInfo,
    ListCoordinations,
    ListCoordinationsRequest,
    ListCoordinationsResponse,
)
from .list_drafts_of_company import ListDraftsOfCompany, ListDraftsResponse
from .list_inbound_coop_requests import (
    ListedInboundCoopRequest,
    ListInboundCoopRequests,
    ListInboundCoopRequestsRequest,
    ListInboundCoopRequestsResponse,
)
from .list_messages import (
    ListedMessage,
    ListMessages,
    ListMessagesRequest,
    ListMessagesResponse,
)
from .list_outbound_coop_requests import (
    ListedOutboundCoopRequest,
    ListOutboundCoopRequests,
    ListOutboundCoopRequestsRequest,
    ListOutboundCoopRequestsResponse,
)
from .list_plans import ListedPlan, ListPlans, ListPlansResponse
from .list_workers import ListedWorker, ListWorkers, ListWorkersResponse
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
from .register_company import (
    RegisterCompany,
    RegisterCompanyRequest,
    RegisterCompanyResponse,
)
from .register_member import (
    RegisterMember,
    RegisterMemberRequest,
    RegisterMemberResponse,
)
from .request_cooperation import (
    RequestCooperation,
    RequestCooperationRequest,
    RequestCooperationResponse,
)
from .resend_confirmation_mail import (
    ResendConfirmationMail,
    ResendConfirmationMailRequest,
    ResendConfirmationMailResponse,
)
from .seek_approval import SeekApproval
from .send_work_certificates_to_worker import SendWorkCertificatesToWorker
from .show_my_plans import ShowMyPlansRequest, ShowMyPlansResponse, ShowMyPlansUseCase
from .show_p_account_details import ShowPAccountDetails, ShowPAccountDetailsResponse
from .show_r_account_details import ShowRAccountDetails, ShowRAccountDetailsResponse
from .show_work_invites import ShowWorkInvites, ShowWorkInvitesRequest
from .toggle_product_availablity import (
    ToggleProductAvailability,
    ToggleProductAvailabilityResponse,
)
from .update_plans_and_payout import UpdatePlansAndPayout

__all__ = [
    "AcceptCooperation",
    "AcceptCooperationRequest",
    "AcceptCooperationResponse",
    "ActivatePlanAndGrantCredit",
    "AnswerCompanyWorkInvite",
    "AnswerCompanyWorkInviteRequest",
    "AnswerCompanyWorkInviteResponse",
    "CancelCooperationSolicitation",
    "CancelCooperationSolicitationRequest",
    "CheckForUnreadMessages",
    "CheckForUnreadMessagesRequest",
    "CheckForUnreadMessagesResponse",
    "CompanyFilter",
    "CompanyQueryResponse",
    "ConfirmMemberUseCase",
    "CooperationInfo",
    "CooperationInfo",
    "CreateCooperation",
    "CreateCooperationRequest",
    "CreateCooperationResponse",
    "CreatePlanDraft",
    "CreatePlanDraftRequest",
    "CreatePlanDraftResponse",
    "DenyCooperation",
    "DenyCooperationRequest",
    "DenyCooperationResponse",
    "DraftQueryResponse",
    "DraftSummaryResponse",
    "DraftSummarySuccess",
    "EndCooperation",
    "EndCooperationRequest",
    "EndCooperationResponse",
    "GetCompanySummary",
    "GetCompanySummaryResponse",
    "GetCompanySummarySuccess",
    "GetCoopSummary",
    "GetCoopSummaryRequest",
    "GetCoopSummaryResponse",
    "GetCoopSummarySuccess",
    "GetDraftSummary",
    "GetMemberAccount",
    "GetMemberAccountResponse",
    "GetMemberProfileInfo",
    "GetMemberProfileInfoResponse",
    "GetPlanSummary",
    "GetStatistics",
    "GetCompanyTransactions",
    "HidePlan",
    "HidePlanResponse",
    "InviteWorkerToCompany",
    "InviteWorkerToCompanyRequest",
    "ListAllCooperations",
    "ListAllCooperationsResponse",
    "ListCoordinations",
    "ListCoordinationsRequest",
    "ListCoordinationsResponse",
    "ListDraftsOfCompany",
    "ListDraftsResponse",
    "ListInboundCoopRequests",
    "ListInboundCoopRequestsRequest",
    "ListInboundCoopRequestsResponse",
    "ListMessages",
    "ListMessagesRequest",
    "ListMessagesResponse",
    "ListOutboundCoopRequests",
    "ListOutboundCoopRequestsRequest",
    "ListOutboundCoopRequestsResponse",
    "ListPlans",
    "ListPlansResponse",
    "ListWorkers",
    "ListWorkersResponse",
    "ListedCooperation",
    "ListedInboundCoopRequest",
    "ListedMessage",
    "ListedOutboundCoopRequest",
    "ListedPlan",
    "ListedWorker",
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
    "ReadMessage",
    "ReadMessageFailure",
    "ReadMessageRequest",
    "ReadMessageResponse",
    "ReadMessageSuccess",
    "RegisterCompany",
    "RegisterCompanyRequest",
    "RegisterCompanyResponse",
    "RegisterMember",
    "RegisterMemberRequest",
    "RegisterMemberResponse",
    "RequestCooperation",
    "RequestCooperationRequest",
    "RequestCooperationResponse",
    "ResendConfirmationMail",
    "ResendConfirmationMailRequest",
    "ResendConfirmationMailResponse",
    "SeekApproval",
    "SendWorkCertificatesToWorker",
    "ShowPAccountDetails",
    "ShowPAccountDetailsResponse",
    "ShowRAccountDetails",
    "ShowRAccountDetailsResponse",
    "ShowMyPlansRequest",
    "ShowMyPlansResponse",
    "ShowMyPlansUseCase",
    "ShowWorkInvites",
    "ShowWorkInvitesRequest",
    "StatisticsResponse",
    "ToggleProductAvailability",
    "ToggleProductAvailabilityResponse",
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
