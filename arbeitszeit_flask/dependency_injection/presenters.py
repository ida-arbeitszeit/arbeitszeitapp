from injector import Module, provider

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.url_index import CompanyUrlIndex, MemberUrlIndex
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.pay_means_of_production import PayMeansOfProductionPresenter
from arbeitszeit_web.presenters.end_cooperation_presenter import EndCooperationPresenter
from arbeitszeit_web.presenters.get_member_dashboard_presenter import (
    GetMemberDashboardPresenter,
)
from arbeitszeit_web.presenters.send_work_certificates_to_worker_presenter import (
    SendWorkCertificatesToWorkerPresenter,
)
from arbeitszeit_web.presenters.show_a_account_details_presenter import (
    ShowAAccountDetailsPresenter,
)
from arbeitszeit_web.presenters.show_p_account_details_presenter import (
    ShowPAccountDetailsPresenter,
)
from arbeitszeit_web.presenters.show_prd_account_details_presenter import (
    ShowPRDAccountDetailsPresenter,
)
from arbeitszeit_web.presenters.show_r_account_details_presenter import (
    ShowRAccountDetailsPresenter,
)
from arbeitszeit_web.request_cooperation import RequestCooperationPresenter
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import (
    CoopSummaryUrlIndex,
    InviteUrlIndex,
    PlanSummaryUrlIndex,
    PlotsUrlIndex,
)


class MemberPresenterModule(Module):
    @provider
    def provide_get_member_dashboard_presenter(
        self,
        translator: Translator,
        url_index: MemberUrlIndex,
        datetime_service: DatetimeService,
        invite_url_index: InviteUrlIndex,
    ) -> GetMemberDashboardPresenter:
        return GetMemberDashboardPresenter(
            translator=translator,
            url_index=url_index,
            datetime_service=datetime_service,
            invite_url_index=invite_url_index,
        )


class CompanyPresenterModule(Module):
    @provider
    def provide_pay_means_of_production_presenter(
        self, notifier: Notifier, trans: Translator, company_url_index: CompanyUrlIndex
    ) -> PayMeansOfProductionPresenter:
        return PayMeansOfProductionPresenter(
            notifier, trans, pay_means_of_production_url_index=company_url_index
        )

    @provider
    def provide_request_cooperation_presenter(
        self, translator: Translator
    ) -> RequestCooperationPresenter:
        return RequestCooperationPresenter(translator)

    @provider
    def provide_send_work_certificates_to_worker_presenter(
        self, notifier: Notifier, translator: Translator
    ) -> SendWorkCertificatesToWorkerPresenter:
        return SendWorkCertificatesToWorkerPresenter(notifier, translator)

    @provider
    def provide_end_cooperation_presenter(
        self,
        request: FlaskRequest,
        notifier: Notifier,
        plan_summary_index: PlanSummaryUrlIndex,
        coop_summary_index: CoopSummaryUrlIndex,
        translator: Translator,
    ) -> EndCooperationPresenter:
        return EndCooperationPresenter(
            request, notifier, plan_summary_index, coop_summary_index, translator
        )

    @provider
    def provide_show_prd_account_details_presenter(
        self,
        translator: Translator,
        url_index: PlotsUrlIndex,
        datetime_service: DatetimeService,
    ) -> ShowPRDAccountDetailsPresenter:
        return ShowPRDAccountDetailsPresenter(
            translator=translator,
            url_index=url_index,
            datetime_service=datetime_service,
        )

    @provider
    def provide_show_r_account_details_presenter(
        self,
        translator: Translator,
        url_index: PlotsUrlIndex,
        datetime_service: DatetimeService,
    ) -> ShowRAccountDetailsPresenter:
        return ShowRAccountDetailsPresenter(
            trans=translator, url_index=url_index, datetime_service=datetime_service
        )

    @provider
    def provide_show_a_account_details_presenter(
        self,
        translator: Translator,
        url_index: PlotsUrlIndex,
        datetime_service: DatetimeService,
    ) -> ShowAAccountDetailsPresenter:
        return ShowAAccountDetailsPresenter(
            trans=translator, url_index=url_index, datetime_service=datetime_service
        )

    @provider
    def provide_show_p_account_details_presenter(
        self,
        translator: Translator,
        url_index: PlotsUrlIndex,
        datetime_service: DatetimeService,
    ) -> ShowPAccountDetailsPresenter:
        return ShowPAccountDetailsPresenter(
            trans=translator, url_index=url_index, datetime_service=datetime_service
        )


class PresenterModule(Module):
    pass
