from injector import Injector, Module, provider, singleton

from arbeitszeit_web.answer_company_work_invite import AnswerCompanyWorkInvitePresenter
from arbeitszeit_web.create_cooperation import CreateCooperationPresenter
from arbeitszeit_web.get_coop_summary import GetCoopSummarySuccessPresenter
from arbeitszeit_web.get_member_profile_info import GetMemberProfileInfoPresenter
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.presenters.end_cooperation_presenter import EndCooperationPresenter
from arbeitszeit_web.url_index import ListMessagesUrlIndex
from tests.request import FakeRequest
from tests.translator import FakeTranslator

from .notifier import NotifierTestImpl
from .url_index import (
    CoopSummaryUrlIndexTestImpl,
    EndCoopUrlIndexTestImpl,
    ListMessageUrlIndexTestImpl,
    PlanSummaryUrlIndexTestImpl,
)


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


def get_dependency_injector() -> Injector:
    return Injector(modules=[PresenterTestsInjector()])
