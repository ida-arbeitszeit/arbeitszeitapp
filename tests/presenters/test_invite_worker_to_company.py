from unittest import TestCase

from arbeitszeit.use_cases.invite_worker_to_company import InviteWorkerToCompanyUseCase
from arbeitszeit_web.www.presenters.invite_worker_to_company_presenter import (
    InviteWorkerToCompanyPresenter,
)
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector


class InviteWorkerToCompanyPresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.translator = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(InviteWorkerToCompanyPresenter)

    def test_successfule_invitation_response_displays_proper_notification(self) -> None:
        response = InviteWorkerToCompanyUseCase.Response(
            is_success=True,
        )
        view_model = self.presenter.present(response)
        self.assertIn(
            self.translator.gettext("Worker has been invited successfully."),
            view_model.notifications,
        )

    def test_unsuccessful_invitation_response_displays_proper_message(self) -> None:
        response = InviteWorkerToCompanyUseCase.Response(
            is_success=False,
        )
        view_model = self.presenter.present(response)
        self.assertIn(
            self.translator.gettext("Worker could not be invited."),
            view_model.notifications,
        )
