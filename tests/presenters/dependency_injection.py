from injector import Injector, Module, provider, singleton

from arbeitszeit_web.answer_company_work_invite import AnswerCompanyWorkInvitePresenter
from arbeitszeit_web.create_cooperation import CreateCooperationPresenter
from arbeitszeit_web.get_company_summary import GetCompanySummarySuccessPresenter
from arbeitszeit_web.get_coop_summary import GetCoopSummarySuccessPresenter
from arbeitszeit_web.get_member_profile_info import GetMemberProfileInfoPresenter
from arbeitszeit_web.get_plan_summary_company import (
    GetPlanSummaryCompanySuccessPresenter,
)
from arbeitszeit_web.get_statistics import GetStatisticsPresenter
from arbeitszeit_web.hide_plan import HidePlanPresenter
from arbeitszeit_web.list_all_cooperations import ListAllCooperationsPresenter
from arbeitszeit_web.list_messages import ListMessagesPresenter
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.pay_consumer_product import PayConsumerProductPresenter
from arbeitszeit_web.pay_means_of_production import PayMeansOfProductionPresenter
from arbeitszeit_web.plan_summary_service import (
    PlanSummaryService,
    PlanSummaryServiceImpl,
)
from arbeitszeit_web.presenters.end_cooperation_presenter import EndCooperationPresenter
from arbeitszeit_web.query_companies import QueryCompaniesPresenter
from arbeitszeit_web.query_plans import QueryPlansPresenter
from arbeitszeit_web.read_message import ReadMessagePresenter
from arbeitszeit_web.url_index import ListMessagesUrlIndex
from tests.request import FakeRequest
from tests.translator import FakeTranslator

from .notifier import NotifierTestImpl
from .url_index import (
    CompanySummaryUrlIndex,
    CoopSummaryUrlIndexTestImpl,
    EndCoopUrlIndexTestImpl,
    ListMessageUrlIndexTestImpl,
    MessageUrlIndex,
    PlanSummaryUrlIndexTestImpl,
    TogglePlanAvailabilityUrlIndex,
)
from .user_action_resolver import UserActionResolver


class PresenterTestsInjector(Module):
    @singleton
    @provider
    def provide_fake_request(self) -> FakeRequest:
        return FakeRequest()

    @singleton
    @provider
    def provide_notifier_test_impl(self) -> NotifierTestImpl:
        return NotifierTestImpl()

    @provider
    def provide_notifier(self, notifier: NotifierTestImpl) -> Notifier:
        return notifier

    @provider
    def provide_list_messages_url_index_test_impl(self) -> ListMessageUrlIndexTestImpl:
        return ListMessageUrlIndexTestImpl()

    @singleton
    @provider
    def provide_toggle_plan_availability_url_index(
        self,
    ) -> TogglePlanAvailabilityUrlIndex:
        return TogglePlanAvailabilityUrlIndex()

    @provider
    def provide_list_messages_url_index(
        self, url_index: ListMessageUrlIndexTestImpl
    ) -> ListMessagesUrlIndex:
        return url_index

    @singleton
    @provider
    def provide_plan_summary_url_index_test_impl(self) -> PlanSummaryUrlIndexTestImpl:
        return PlanSummaryUrlIndexTestImpl()

    @singleton
    @provider
    def provide_coop_summary_url_index_test_impl(self) -> CoopSummaryUrlIndexTestImpl:
        return CoopSummaryUrlIndexTestImpl()

    @provider
    def provide_answer_company_work_invite_presenter(
        self,
        notifier: Notifier,
        url_index: ListMessagesUrlIndex,
        translator: FakeTranslator,
    ) -> AnswerCompanyWorkInvitePresenter:
        return AnswerCompanyWorkInvitePresenter(
            user_notifier=notifier,
            url_index=url_index,
            translator=translator,
        )

    @provider
    def provide_create_cooperation_presenter(
        self, notifier: Notifier, translator: FakeTranslator
    ) -> CreateCooperationPresenter:
        return CreateCooperationPresenter(
            user_notifier=notifier,
            translator=translator,
        )

    @provider
    def provide_end_cooperation_presenter(
        self,
        request: FakeRequest,
        notifier: Notifier,
        plan_summary_index: PlanSummaryUrlIndexTestImpl,
        coop_summary_index: CoopSummaryUrlIndexTestImpl,
    ) -> EndCooperationPresenter:
        return EndCooperationPresenter(
            request=request,
            notifier=notifier,
            plan_summary_index=plan_summary_index,
            coop_summary_index=coop_summary_index,
        )

    @provider
    def provide_get_coop_summary_success_presenter(
        self,
        plan_url_index: PlanSummaryUrlIndexTestImpl,
        end_coop_url_index: EndCoopUrlIndexTestImpl,
    ) -> GetCoopSummarySuccessPresenter:
        return GetCoopSummarySuccessPresenter(
            plan_url_index=plan_url_index,
            end_coop_url_index=end_coop_url_index,
        )

    @provider
    def provide_get_member_profile_info_presenter(
        self, translator: FakeTranslator
    ) -> GetMemberProfileInfoPresenter:
        return GetMemberProfileInfoPresenter(
            translator=translator,
        )

    @provider
    def provide_get_company_summary_success_presenter(
        self, plan_index: PlanSummaryUrlIndexTestImpl, translator: FakeTranslator
    ) -> GetCompanySummarySuccessPresenter:
        return GetCompanySummarySuccessPresenter(
            plan_index=plan_index, translator=translator
        )

    @provider
    def provide_plan_summary_service(
        self,
        coop_url_index: CoopSummaryUrlIndexTestImpl,
        company_url_index: CompanySummaryUrlIndex,
        translator: FakeTranslator,
    ) -> PlanSummaryService:
        return PlanSummaryServiceImpl(
            coop_url_index=coop_url_index,
            company_url_index=company_url_index,
            trans=translator,
        )

    @provider
    def provide_get_plan_summary_company_success_presenter(
        self,
        toggle_availability_url_index: TogglePlanAvailabilityUrlIndex,
        end_coop_url_index: EndCoopUrlIndexTestImpl,
        translator: FakeTranslator,
        plan_summary_service: PlanSummaryService,
    ) -> GetPlanSummaryCompanySuccessPresenter:
        return GetPlanSummaryCompanySuccessPresenter(
            toggle_availability_url_index=toggle_availability_url_index,
            end_coop_url_index=end_coop_url_index,
            trans=translator,
            plan_summary_service=plan_summary_service,
        )

    @provider
    def provide_get_statistics_presenter(
        self, translator: FakeTranslator
    ) -> GetStatisticsPresenter:
        return GetStatisticsPresenter(translator=translator)

    @provider
    def provide_list_all_cooperations_presenter(
        self, coop_summary_url_index: CoopSummaryUrlIndexTestImpl
    ) -> ListAllCooperationsPresenter:
        return ListAllCooperationsPresenter(
            coop_url_index=coop_summary_url_index,
        )

    @provider
    def provide_hide_plan_presenter(
        self, notifier: Notifier, translator: FakeTranslator
    ) -> HidePlanPresenter:
        return HidePlanPresenter(
            notifier=notifier,
            trans=translator,
        )

    @provider
    def provide_list_messages_presenter(
        self, messages_url_index: MessageUrlIndex
    ) -> ListMessagesPresenter:
        return ListMessagesPresenter(url_index=messages_url_index)

    @provider
    def provide_pay_consumer_product_presenter(
        self, notifier: Notifier, translator: FakeTranslator
    ) -> PayConsumerProductPresenter:
        return PayConsumerProductPresenter(
            user_notifier=notifier,
            translator=translator,
        )

    @provider
    def provide_pay_means_of_production_presenter(
        self, notifier: Notifier, translator: FakeTranslator
    ) -> PayMeansOfProductionPresenter:
        return PayMeansOfProductionPresenter(
            user_notifier=notifier,
            trans=translator,
        )

    @provider
    def provide_plan_summary_service_impl(
        self,
        coop_url_index: CoopSummaryUrlIndexTestImpl,
        company_url_index: CompanySummaryUrlIndex,
        translator: FakeTranslator,
    ) -> PlanSummaryServiceImpl:
        return PlanSummaryServiceImpl(
            coop_url_index=coop_url_index,
            company_url_index=company_url_index,
            trans=translator,
        )

    @provider
    def provide_query_companies_presenter(
        self, notifier: Notifier, company_url_index: CompanySummaryUrlIndex
    ) -> QueryCompaniesPresenter:
        return QueryCompaniesPresenter(
            user_notifier=notifier,
            company_url_index=company_url_index,
        )

    @provider
    def provide_query_plans_presenter(
        self,
        notifier: Notifier,
        coop_url_index: CoopSummaryUrlIndexTestImpl,
        plan_url_index: PlanSummaryUrlIndexTestImpl,
        company_url_index: CompanySummaryUrlIndex,
        translator: FakeTranslator,
    ) -> QueryPlansPresenter:
        return QueryPlansPresenter(
            plan_url_index=plan_url_index,
            company_url_index=company_url_index,
            coop_url_index=coop_url_index,
            user_notifier=notifier,
            trans=translator,
        )

    @provider
    def provide_read_message_presenter(
        self, user_action_resolver: UserActionResolver
    ) -> ReadMessagePresenter:
        return ReadMessagePresenter(
            action_link_resolver=user_action_resolver,
        )


def get_dependency_injector() -> Injector:
    return Injector(modules=[PresenterTestsInjector()])
