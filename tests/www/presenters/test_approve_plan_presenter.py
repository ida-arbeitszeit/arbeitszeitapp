from arbeitszeit.use_cases.approve_plan import ApprovePlanUseCase as UseCase
from arbeitszeit_web.www.presenters.approve_plan_presenter import ApprovePlanPresenter
from tests.translator import FakeTranslator
from tests.www.presenters.notifier import NotifierTestImpl

from .base_test_case import BaseTestCase
from .url_index import UrlIndexTestImpl


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ApprovePlanPresenter)
        self.url_index = self.injector.get(UrlIndexTestImpl)
        self.notifier = self.injector.get(NotifierTestImpl)
        self.translator = self.injector.get(FakeTranslator)

    def test_that_view_model_redirects_to_list_view_for_unreviewed_plans(self) -> None:
        response = UseCase.Response(is_approved=True)
        view_model = self.presenter.approve_plan(response)
        assert (
            view_model.redirect_url
            == self.url_index.get_unreviewed_plans_list_view_url()
        )

    def test_that_user_gets_info_message_when_approval_was_a_success(self) -> None:
        response = UseCase.Response(is_approved=True)
        self.presenter.approve_plan(response)
        assert self.notifier.infos

    def test_that_user_does_not_get_warning_on_success(self) -> None:
        response = UseCase.Response(is_approved=True)
        self.presenter.approve_plan(response)
        assert not self.notifier.warnings

    def test_that_user_gets_correct_info_message_when_approval_was_successful(
        self,
    ) -> None:
        response = UseCase.Response(is_approved=True)
        self.presenter.approve_plan(response)
        assert self.notifier.infos[0] == self.translator.gettext(
            "Plan was approved successfully"
        )

    def test_that_user_gets_warning_message_when_approval_failed(self) -> None:
        response = UseCase.Response(is_approved=False)
        self.presenter.approve_plan(response)
        assert self.notifier.warnings

    def test_that_user_does_not_get_info_message_when_approval_failed(self) -> None:
        response = UseCase.Response(is_approved=False)
        self.presenter.approve_plan(response)
        assert not self.notifier.infos

    def test_that_user_gets_correct_warning_message_when_approval_failed(self) -> None:
        response = UseCase.Response(is_approved=False)
        self.presenter.approve_plan(response)
        assert self.notifier.warnings[0] == self.translator.gettext(
            "Plan approval failed"
        )
