from typing import List
from uuid import uuid4

from arbeitszeit.interactors.end_cooperation import EndCooperationResponse
from arbeitszeit_web.session import UserRole
from arbeitszeit_web.www.presenters.end_cooperation_presenter import (
    EndCooperationPresenter,
)
from tests.request import FakeRequest
from tests.www.base_test_case import BaseTestCase

SUCCESSFUL_RESPONSE = EndCooperationResponse(rejection_reason=None)

REJECTED_RESPONSE_PLAN_NOT_FOUND = EndCooperationResponse(
    rejection_reason=EndCooperationResponse.RejectionReason.plan_not_found,
)

REJECTED_RESPONSE_COOPERATION_NOT_FOUND = EndCooperationResponse(
    rejection_reason=EndCooperationResponse.RejectionReason.cooperation_not_found,
)


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(EndCooperationPresenter)
        self.session.login_company(company=uuid4())

    def test_404_and_empty_url_returned_when_interactor_response_returned_plan_not_found(
        self,
    ) -> None:
        request = FakeRequest()
        view_model = self.presenter.present(
            REJECTED_RESPONSE_PLAN_NOT_FOUND, web_request=request
        )
        self.assertTrue(view_model.show_404)
        self.assertFalse(view_model.redirect_url)

    def test_notification_returned_when_operation_was_rejected_because_plan_was_not_found(
        self,
    ) -> None:
        request = FakeRequest()
        self.presenter.present(REJECTED_RESPONSE_PLAN_NOT_FOUND, web_request=request)
        self.assertTrue(self._get_warning_notifications())

    def test_correct_notification_is_returned_when_operation_was_rejected_because_plan_was_not_found(
        self,
    ) -> None:
        request = FakeRequest()
        self.presenter.present(REJECTED_RESPONSE_PLAN_NOT_FOUND, web_request=request)
        self.assertIn(
            self.translator.gettext("Cooperation could not be terminated."),
            self._get_warning_notifications(),
        )

    def test_url_gets_returned_when_interactor_response_is_successfull(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_arg("plan_id", str(uuid4()))
        request.set_arg("cooperation_id", str(uuid4()))
        view_model = self.presenter.present(SUCCESSFUL_RESPONSE, web_request=request)
        self.assertFalse(view_model.show_404)
        self.assertTrue(view_model.redirect_url)

    def test_coop_summary_url_gets_returned_as_default_when_no_referer_is_given(
        self,
    ) -> None:
        request = FakeRequest()
        coop_id = uuid4()
        request.set_arg("plan_id", str(uuid4()))
        request.set_arg("cooperation_id", str(coop_id))
        view_model = self.presenter.present(SUCCESSFUL_RESPONSE, web_request=request)
        self.assertFalse(view_model.show_404)
        self.assertEqual(
            view_model.redirect_url,
            self.url_index.get_coop_summary_url(coop_id=coop_id),
        )

    def test_plan_details_url_gets_returned_when_plan_details_url_was_referer(
        self,
    ) -> None:
        request = FakeRequest()
        plan_id = uuid4()
        request.set_header("Referer", f"/company/plan_details/{str(plan_id)}")
        request.set_arg("plan_id", str(plan_id))
        request.set_arg("cooperation_id", str(uuid4()))
        view_model = self.presenter.present(SUCCESSFUL_RESPONSE, web_request=request)
        self.assertFalse(view_model.show_404)
        self.assertEqual(
            view_model.redirect_url,
            self.url_index.get_plan_details_url(
                user_role=UserRole.company, plan_id=plan_id
            ),
        )

    def test_correct_notification_is_returned_when_operation_was_successfull(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_arg("plan_id", str(uuid4()))
        request.set_arg("cooperation_id", str(uuid4()))
        self.presenter.present(SUCCESSFUL_RESPONSE, web_request=request)
        self.assertIn(
            self.translator.gettext("Cooperation has been terminated."),
            self._get_info_notifications(),
        )

    def _get_info_notifications(self) -> List[str]:
        return self.notifier.infos

    def _get_warning_notifications(self) -> List[str]:
        return self.notifier.warnings
