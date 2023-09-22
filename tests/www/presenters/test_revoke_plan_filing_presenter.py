from uuid import uuid4

from arbeitszeit.use_cases.revoke_plan_filing import RevokePlanFilingUseCase
from arbeitszeit_web.www.presenters.revoke_plan_filing_presenter import (
    RevokePlanFilingPresenter,
)
from tests.www.base_test_case import BaseTestCase


class RevokePlanFilingPresenterTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RevokePlanFilingPresenter)

    def test_warning_is_displayed_when_revoking_failed(self) -> None:
        response = self.get_use_case_response(rejected=True)
        self.presenter.present(use_case_response=response)
        assert self.notifier.warnings

    def test_info_message_is_displayed_when_revoking_succeeded(self) -> None:
        response = self.get_use_case_response(rejected=False)
        self.presenter.present(use_case_response=response)
        assert self.notifier.infos

    def get_use_case_response(
        self, *, rejected: bool
    ) -> RevokePlanFilingUseCase.Response:
        if rejected:
            return RevokePlanFilingUseCase.Response(
                plan_draft=None,
                rejection_reason=RevokePlanFilingUseCase.Response.RejectionReason.plan_not_found,
            )
        else:
            return RevokePlanFilingUseCase.Response(
                plan_draft=uuid4(), rejection_reason=None
            )
