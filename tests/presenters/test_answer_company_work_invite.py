from typing import Optional
from unittest import TestCase

from arbeitszeit.use_cases import AnswerCompanyWorkInviteResponse
from arbeitszeit_web.answer_company_work_invite import AnswerCompanyWorkInvitePresenter

from .notifier import NotifierTestImpl

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


class SuccessfulResponseTests(TestCase):
    def setUp(self) -> None:
        self.notifier = NotifierTestImpl()
        self.presenter = AnswerCompanyWorkInvitePresenter(user_notifier=self.notifier)

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
            f'Erfolgreich dem Betrieb "{COMPANY_NAME}" beigetreten',
            self.notifier.infos,
        )

    def test_proper_info_message_is_displayed_when_rejecting_an_invite(self) -> None:
        self.presenter.present(
            get_response(is_accepted=False, company_name=COMPANY_NAME)
        )
        self.assertIn(
            f'Einladung zum Betrieb "{COMPANY_NAME}" abgelehnt',
            self.notifier.infos,
        )

    def test_only_one_info_message_is_displayed_when_accepting_an_invite(self) -> None:
        self.presenter.present(get_response(is_accepted=True))
        self.assertEqual(len(self.notifier.infos), 1)

    def test_only_one_info_message_is_displayed_when_rejecting_an_invite(self) -> None:
        self.presenter.present(get_response(is_accepted=False))
        self.assertEqual(len(self.notifier.infos), 1)


class UnsuccessfulResponseTests(TestCase):
    def setUp(self) -> None:
        self.notifier = NotifierTestImpl()
        self.presenter = AnswerCompanyWorkInvitePresenter(user_notifier=self.notifier)

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
            "Annehmen oder Ablehnen dieser Einladung ist nicht möglich",
            self.notifier.warnings,
        )
