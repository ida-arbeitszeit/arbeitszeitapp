from uuid import uuid4

from arbeitszeit.use_cases.invite_worker_to_company import InviteWorkerToCompanyUseCase
from arbeitszeit_web.www.presenters.invite_worker_to_company_presenter import (
    InviteWorkerToCompanyPresenter,
)
from tests.www.base_test_case import BaseTestCase


class InviteWorkerToCompanyPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(InviteWorkerToCompanyPresenter)

    def test_when_worker_is_not_found_code_400_is_presented(self):
        response = InviteWorkerToCompanyUseCase.Response(
            worker=uuid4(),
            rejection_reason=InviteWorkerToCompanyUseCase.Response.RejectionReason.WORKER_NOT_FOUND,
        )
        view_model = self.presenter.present(response)
        assert view_model.worker == str(response.worker)

    def test_when_worker_is_not_found_worker_id_from_response_is_presented(self):
        response = InviteWorkerToCompanyUseCase.Response(
            worker=uuid4(),
            rejection_reason=InviteWorkerToCompanyUseCase.Response.RejectionReason.WORKER_NOT_FOUND,
        )
        view_model = self.presenter.present(response)
        assert view_model.worker == str(response.worker)

    def test_when_worker_is_not_found_warning_is_presented(self):
        response = InviteWorkerToCompanyUseCase.Response(
            worker=uuid4(),
            rejection_reason=InviteWorkerToCompanyUseCase.Response.RejectionReason.WORKER_NOT_FOUND,
        )
        self.presenter.present(response)
        assert self.notifier.warnings[0] == self.translator.gettext(
            "Worker could not be found."
        )

    def test_when_company_is_not_found_code_400_is_presented(self):
        response = InviteWorkerToCompanyUseCase.Response(
            worker=uuid4(),
            rejection_reason=InviteWorkerToCompanyUseCase.Response.RejectionReason.COMPANY_NOT_FOUND,
        )
        view_model = self.presenter.present(response)
        assert view_model.status_code == 400

    def test_when_company_is_not_found_worker_id_from_response_is_presented(self):
        response = InviteWorkerToCompanyUseCase.Response(
            worker=uuid4(),
            rejection_reason=InviteWorkerToCompanyUseCase.Response.RejectionReason.COMPANY_NOT_FOUND,
        )
        view_model = self.presenter.present(response)
        assert view_model.worker == str(response.worker)

    def test_when_company_is_not_found_warning_is_presented(self):
        response = InviteWorkerToCompanyUseCase.Response(
            worker=uuid4(),
            rejection_reason=InviteWorkerToCompanyUseCase.Response.RejectionReason.COMPANY_NOT_FOUND,
        )
        self.presenter.present(response)
        assert self.notifier.warnings[0] == self.translator.gettext(
            "Company could not be found."
        )

    def test_when_worker_works_already_for_company_code_400_is_presented(self):
        response = InviteWorkerToCompanyUseCase.Response(
            worker=uuid4(),
            rejection_reason=InviteWorkerToCompanyUseCase.Response.RejectionReason.WORKER_ALREADY_WORKS_FOR_COMPANY,
        )
        view_model = self.presenter.present(response)
        assert view_model.status_code == 400

    def test_when_worker_works_already_for_company_worker_id_from_response_is_presented(
        self,
    ):
        response = InviteWorkerToCompanyUseCase.Response(
            worker=uuid4(),
            rejection_reason=InviteWorkerToCompanyUseCase.Response.RejectionReason.WORKER_ALREADY_WORKS_FOR_COMPANY,
        )
        view_model = self.presenter.present(response)
        assert view_model.worker == str(response.worker)

    def test_when_worker_works_already_for_company_warning_is_presented(self):
        response = InviteWorkerToCompanyUseCase.Response(
            worker=uuid4(),
            rejection_reason=InviteWorkerToCompanyUseCase.Response.RejectionReason.WORKER_ALREADY_WORKS_FOR_COMPANY,
        )
        self.presenter.present(response)
        assert self.notifier.warnings[0] == self.translator.gettext(
            "Worker already works for the company."
        )

    def test_when_invitation_is_already_issued_code_400_is_presented(self):
        response = InviteWorkerToCompanyUseCase.Response(
            worker=uuid4(),
            rejection_reason=InviteWorkerToCompanyUseCase.Response.RejectionReason.INVITATION_ALREADY_ISSUED,
        )
        view_model = self.presenter.present(response)
        assert view_model.status_code == 400

    def test_when_invitation_is_already_issued_worker_id_from_response_is_presented(
        self,
    ):
        response = InviteWorkerToCompanyUseCase.Response(
            worker=uuid4(),
            rejection_reason=InviteWorkerToCompanyUseCase.Response.RejectionReason.INVITATION_ALREADY_ISSUED,
        )
        view_model = self.presenter.present(response)
        assert view_model.worker == str(response.worker)

    def test_when_invitation_is_already_issued_warning_is_presented(self):
        response = InviteWorkerToCompanyUseCase.Response(
            worker=uuid4(),
            rejection_reason=InviteWorkerToCompanyUseCase.Response.RejectionReason.INVITATION_ALREADY_ISSUED,
        )
        self.presenter.present(response)
        assert self.notifier.warnings[0] == self.translator.gettext(
            "Invitation has already been issued."
        )

    def test_when_worker_is_invited_code_302_is_presented(self):
        response = InviteWorkerToCompanyUseCase.Response(
            worker=uuid4(),
        )
        view_model = self.presenter.present(response)
        assert view_model.status_code == 302

    def test_when_worker_is_invited_worker_id_from_response_is_presented(self):
        response = InviteWorkerToCompanyUseCase.Response(
            worker=uuid4(),
        )
        view_model = self.presenter.present(response)
        assert view_model.worker == str(response.worker)

    def test_when_worker_is_invited_info_is_presented(self):
        response = InviteWorkerToCompanyUseCase.Response(
            worker=uuid4(),
        )
        self.presenter.present(response)
        assert self.notifier.infos[0] == self.translator.gettext(
            "Worker has been invited successfully."
        )
