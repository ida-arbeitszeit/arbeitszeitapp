from arbeitszeit.interactors import resend_work_invite
from arbeitszeit_web.www.presenters.resend_work_invite_presenter import (
    ResendWorkInvitePresenter,
)
from tests.www.base_test_case import BaseTestCase


class TestResendWorkInvitePresenter(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.controller = self.injector.get(ResendWorkInvitePresenter)

    def test_warning_is_displayed_when_invite_does_not_exist(self):
        response = self.create_interactor_response(failed=True)
        self.controller.present(response)
        assert len(self.notifier.warnings) == 1
        assert not self.notifier.infos

    def test_correct_warning_is_displayed_when_invite_does_not_exist(self):
        response = self.create_interactor_response(failed=True)
        self.controller.present(response)
        assert self.notifier.warnings[0] == self.translator.gettext(
            "Invite does not exist."
        )

    def test_status_code_is_400_when_invite_does_not_exist(self):
        response = self.create_interactor_response(failed=True)
        view_model = self.controller.present(response)
        assert view_model.status_code == 400

    def test_info_is_displayed_when_invite_has_been_resent_successfully(self):
        response = self.create_interactor_response()
        self.controller.present(response)
        assert len(self.notifier.infos) == 1
        assert not self.notifier.warnings

    def test_correct_info_is_displayed_when_invite_has_been_resent_successfully(self):
        response = self.create_interactor_response()
        self.controller.present(response)
        assert self.notifier.infos[0] == self.translator.gettext(
            "Invite has been resent successfully."
        )

    def test_status_code_is_302_when_invite_has_been_resent_successfully(self):
        response = self.create_interactor_response()
        view_model = self.controller.present(response)
        assert view_model.status_code == 302

    def create_interactor_response(
        self, failed: bool = False
    ) -> resend_work_invite.Response:
        if failed:
            return resend_work_invite.Response(
                rejection_reason=resend_work_invite.Response.RejectionReason.INVITE_DOES_NOT_EXIST
            )
        return resend_work_invite.Response()
