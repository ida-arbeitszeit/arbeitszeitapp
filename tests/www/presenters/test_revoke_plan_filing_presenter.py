from uuid import uuid4

from arbeitszeit.interactors.revoke_plan_filing import RevokePlanFilingInteractor
from arbeitszeit_web.www.presenters.revoke_plan_filing_presenter import (
    RevokePlanFilingPresenter,
)
from tests.www.base_test_case import BaseTestCase


class RevokePlanFilingPresenterTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RevokePlanFilingPresenter)

    def test_warning_is_displayed_when_revoking_failed(self) -> None:
        response = self.get_interactor_response(rejected=True)
        self.presenter.present(interactor_response=response)
        assert self.notifier.warnings

    def test_info_message_is_displayed_when_revoking_succeeded(self) -> None:
        response = self.get_interactor_response(rejected=False)
        self.presenter.present(interactor_response=response)
        assert self.notifier.infos

    def get_interactor_response(
        self, *, rejected: bool
    ) -> RevokePlanFilingInteractor.Response:
        if rejected:
            return RevokePlanFilingInteractor.Response(
                plan_draft=None,
                rejection_reason=RevokePlanFilingInteractor.Response.RejectionReason.plan_not_found,
            )
        else:
            return RevokePlanFilingInteractor.Response(
                plan_draft=uuid4(), rejection_reason=None
            )
