from arbeitszeit.use_cases.reject_plan import RejectPlanUseCase as UseCase
from arbeitszeit_web.www.presenters.reject_plan_presenter import RejectPlanPresenter
from tests.www.base_test_case import BaseTestCase


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RejectPlanPresenter)

    def test_that_view_model_redirects_to_list_view_for_unreviewed_plans(self) -> None:
        response = UseCase.Response(is_rejected=True)
        view_model = self.presenter.reject_plan(response)
        assert (
            view_model.redirect_url
            == self.url_index.get_unreviewed_plans_list_view_url()
        )

    def test_that_user_gets_info_message_when_rejection_was_a_success(self) -> None:
        response = UseCase.Response(is_rejected=True)
        self.presenter.reject_plan(response)
        assert self.notifier.infos

    def test_that_user_does_not_get_warning_on_success(self) -> None:
        response = UseCase.Response(is_rejected=True)
        self.presenter.reject_plan(response)
        assert not self.notifier.warnings

    def test_that_user_gets_correct_info_message_when_rejection_was_successful(
        self,
    ) -> None:
        response = UseCase.Response(is_rejected=True)
        self.presenter.reject_plan(response)
        assert self.notifier.infos[0] == self.translator.gettext(
            "Plan was rejected successfully"
        )

    def test_that_user_gets_warning_message_when_rejection_failed(self) -> None:
        response = UseCase.Response(is_rejected=False)
        self.presenter.reject_plan(response)
        assert self.notifier.warnings

    def test_that_user_does_not_get_info_message_when_rejection_failed(self) -> None:
        response = UseCase.Response(is_rejected=False)
        self.presenter.reject_plan(response)
        assert not self.notifier.infos

    def test_that_user_gets_correct_warning_message_when_rejection_failed(self) -> None:
        response = UseCase.Response(is_rejected=False)
        self.presenter.reject_plan(response)
        assert self.notifier.warnings[0] == self.translator.gettext(
            "Plan rejection failed"
        )
