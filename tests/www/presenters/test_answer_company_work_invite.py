from typing import Optional

from arbeitszeit.use_cases.answer_company_work_invite import (
    AnswerCompanyWorkInviteResponse,
)
from arbeitszeit_web.www.presenters.answer_company_work_invite_presenter import (
    AnswerCompanyWorkInvitePresenter,
)
from tests.translator import FakeTranslator
from tests.www.base_test_case import BaseTestCase

from .notifier import NotifierTestImpl
from .url_index import UrlIndexTestImpl

COMPANY_NAME = "test company"


def get_response(
    is_success: Optional[bool] = None,
    is_accepted: Optional[bool] = None,
    company_name: Optional[str] = None,
) -> AnswerCompanyWorkInviteResponse:
    failure_reason: Optional[AnswerCompanyWorkInviteResponse.Failure] = None
    if is_success is None:
        is_success = True
    if is_accepted is None:
        is_accepted = is_success
    if company_name is None:
        if is_success:
            company_name = COMPANY_NAME
    if not is_success:
        failure_reason = AnswerCompanyWorkInviteResponse.Failure.invite_not_found
    return AnswerCompanyWorkInviteResponse(
        is_success=is_success,
        is_accepted=is_accepted,
        company_name=company_name,
        failure_reason=failure_reason,
    )


class SuccessfulResponseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.notifier = self.injector.get(NotifierTestImpl)
        self.url_index = self.injector.get(UrlIndexTestImpl)
        self.translator = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(AnswerCompanyWorkInvitePresenter)

    def test_info_notification_is_displayed_on_success(self) -> None:
        self.presenter.present(get_response(is_success=True))
        self.assertTrue(self.notifier.infos)

    def test_no_warning_notification_is_displayed_on_success(self) -> None:
        self.presenter.present(get_response(is_success=True))
        self.assertFalse(self.notifier.warnings)

    def test_proper_info_message_is_displayed_when_accepting_an_invite(self) -> None:
        self.presenter.present(
            get_response(is_accepted=True, company_name=COMPANY_NAME)
        )
        self.assertIn(
            self.translator.gettext('You successfully joined "%(company)s".')
            % dict(company=COMPANY_NAME),
            self.notifier.infos,
        )

    def test_proper_info_message_is_displayed_when_rejecting_an_invite(self) -> None:
        self.presenter.present(
            get_response(is_accepted=False, company_name=COMPANY_NAME)
        )
        self.assertIn(
            self.translator.gettext('You rejected the invitation from "%(company)s".')
            % dict(company=COMPANY_NAME),
            self.notifier.infos,
        )

    def test_only_one_info_message_is_displayed_when_accepting_an_invite(self) -> None:
        self.presenter.present(get_response(is_accepted=True))
        self.assertEqual(len(self.notifier.infos), 1)

    def test_only_one_info_message_is_displayed_when_rejecting_an_invite(self) -> None:
        self.presenter.present(get_response(is_accepted=False))
        self.assertEqual(len(self.notifier.infos), 1)

    def test_view_model_redirect_is_set_when_invitation_was_accepted(self) -> None:
        view_model = self.presenter.present(get_response(is_accepted=False))
        self.assertIsNotNone(view_model.redirect_url)

    def test_view_model_redirect_is_set_to_member_dashboard(self) -> None:
        view_model = self.presenter.present(get_response(is_accepted=False))
        self.assertEqual(
            view_model.redirect_url, self.url_index.get_member_dashboard_url()
        )


class UnsuccessfulResponseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.notifier = self.injector.get(NotifierTestImpl)
        self.url_index = self.injector.get(UrlIndexTestImpl)
        self.translator = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(AnswerCompanyWorkInvitePresenter)

    def test_warning_notification_is_displayed_on_failure(self) -> None:
        self.presenter.present(get_response(is_success=False))
        self.assertTrue(self.notifier.warnings)

    def test_no_info_notification_is_displayed_on_failure(self) -> None:
        self.presenter.present(get_response(is_success=False))
        self.assertFalse(self.notifier.infos)

    def test_warning_notification_explains_that_operation_was_unsuccessful(
        self,
    ) -> None:
        self.presenter.present(get_response(is_success=False))
        self.assertIn(
            self.translator.gettext("Accepting or rejecting is not possible."),
            self.notifier.warnings,
        )
