from injector import Injector, Module, provider

from arbeitszeit_web.answer_company_work_invite import AnswerCompanyWorkInviteController
from arbeitszeit_web.controllers.end_cooperation_controller import (
    EndCooperationController,
)
from arbeitszeit_web.controllers.send_work_certificates_to_worker_controller import (
    SendWorkCertificatesToWorkerController,
)
from arbeitszeit_web.controllers.show_company_work_invite_details_controller import (
    ShowCompanyWorkInviteDetailsController,
)
from arbeitszeit_web.controllers.show_my_accounts_controller import (
    ShowMyAccountsController,
)
from arbeitszeit_web.create_draft import CreateDraftController
from arbeitszeit_web.invite_worker_to_company import InviteWorkerToCompanyController
from arbeitszeit_web.pay_consumer_product import PayConsumerProductController
from arbeitszeit_web.request import Request
from arbeitszeit_web.request_cooperation import RequestCooperationController
from tests.dependency_injection import TestingModule
from tests.request import FakeRequest
from tests.session import FakeSession
from tests.translator import FakeTranslator
from tests.use_cases.dependency_injection import InMemoryModule


class ControllerTestsModule(Module):
    @provider
    def provide_request(self) -> Request:
        return FakeRequest()

    @provider
    def provide_answer_company_work_invite_controller(
        self, session: FakeSession
    ) -> AnswerCompanyWorkInviteController:
        return AnswerCompanyWorkInviteController(
            session=session,
        )

    @provider
    def provide_invite_worker_to_company_controller(
        self,
        session: FakeSession,
    ) -> InviteWorkerToCompanyController:
        return InviteWorkerToCompanyController(
            session=session,
        )

    @provider
    def provide_end_cooperation_controller(
        self, session: FakeSession, request: FakeRequest
    ) -> EndCooperationController:
        return EndCooperationController(
            session=session,
            request=request,
        )

    @provider
    def provide_pay_consumer_product_controller(
        self, translator: FakeTranslator
    ) -> PayConsumerProductController:
        return PayConsumerProductController(
            translator=translator,
        )

    @provider
    def provide_request_cooperation_controller(
        self, session: FakeSession, translator: FakeTranslator
    ) -> RequestCooperationController:
        return RequestCooperationController(
            session=session,
            translator=translator,
        )

    @provider
    def provide_send_work_certificates_to_worker_controller(
        self, session: FakeSession, request: FakeRequest
    ) -> SendWorkCertificatesToWorkerController:
        return SendWorkCertificatesToWorkerController(
            session=session,
            request=request,
        )

    @provider
    def provide_show_company_work_invite_details_controller(
        self, session: FakeSession
    ) -> ShowCompanyWorkInviteDetailsController:
        return ShowCompanyWorkInviteDetailsController(session=session)

    @provider
    def provide_show_my_accounts_controller(
        self, session: FakeSession
    ) -> ShowMyAccountsController:
        return ShowMyAccountsController(
            session=session,
        )

    @provider
    def provide_create_draft_controller(
        self, session: FakeSession
    ) -> CreateDraftController:
        return CreateDraftController(session=session)


def get_dependency_injector() -> Injector:
    return Injector([TestingModule(), InMemoryModule(), ControllerTestsModule()])
