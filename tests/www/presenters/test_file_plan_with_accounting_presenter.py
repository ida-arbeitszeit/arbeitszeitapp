from typing import Optional
from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.use_cases.file_plan_with_accounting import FilePlanWithAccounting
from arbeitszeit_web.session import UserRole
from arbeitszeit_web.www.presenters.file_plan_with_accounting_presenter import (
    FilePlanWithAccountingPresenter,
)
from tests.session import FakeSession
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector
from .notifier import NotifierTestImpl
from .url_index import UrlIndexTestImpl


class Tests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.presenter = self.injector.get(FilePlanWithAccountingPresenter)
        self.url_index = self.injector.get(UrlIndexTestImpl)
        self.notifier = self.injector.get(NotifierTestImpl)
        self.translator = self.injector.get(FakeTranslator)
        self.session = self.injector.get(FakeSession)
        self.session.login_company(company=uuid4())

    def test_view_model_has_redirect_url_with_successful_responses(self) -> None:
        view_model = self.presenter.present_response(self.create_success_response())
        self.assertIsNotNone(view_model.redirect_url)

    def test_view_model_has_no_redirect_with_failure_responses(self) -> None:
        view_model = self.presenter.present_response(self.create_failure_response())
        self.assertIsNotNone(view_model.redirect_url)

    def test_user_gets_redirected_to_plan_summary_page_on_successful_response(
        self,
    ) -> None:
        plan_id = uuid4()
        view_model = self.presenter.present_response(
            self.create_success_response(plan_id=plan_id)
        )
        self.assertEqual(
            view_model.redirect_url,
            self.url_index.get_plan_summary_url(
                user_role=UserRole.company, plan_id=plan_id
            ),
        )

    def test_user_gets_redirected_to_my_plans_page_on_failure_response(
        self,
    ) -> None:
        view_model = self.presenter.present_response(self.create_failure_response())
        self.assertEqual(
            view_model.redirect_url,
            self.url_index.get_my_plans_url(),
        )

    def test_that_user_receives_warning_on_failure_response(self) -> None:
        self.presenter.present_response(self.create_failure_response())
        self.assertTrue(self.notifier.warnings)

    def test_that_user_receives_no_warning_on_success_response(self) -> None:
        self.presenter.present_response(self.create_success_response())
        self.assertFalse(self.notifier.warnings)

    def test_that_user_receives_info_notification_on_success_response(self) -> None:
        self.presenter.present_response(self.create_success_response())
        self.assertTrue(self.notifier.infos)

    def test_that_user_receives_no_info_notification_on_failure_response(self) -> None:
        self.presenter.present_response(self.create_failure_response())
        self.assertFalse(self.notifier.infos)

    def test_proper_failure_message_on_failure_response(self) -> None:
        self.presenter.present_response(self.create_failure_response())
        self.assertEqual(
            self.translator.gettext("Could not file plan with social accounting"),
            self.notifier.warnings[0],
        )

    def test_proper_info_message_on_success_response(self) -> None:
        self.presenter.present_response(self.create_success_response())
        self.assertEqual(
            self.translator.gettext("Successfully filed plan with social accounting"),
            self.notifier.infos[0],
        )

    def create_success_response(
        self, plan_id: Optional[UUID] = None
    ) -> FilePlanWithAccounting.Response:
        if plan_id is None:
            plan_id = uuid4()
        return FilePlanWithAccounting.Response(
            is_plan_successfully_filed=True,
            plan_id=plan_id,
        )

    def create_failure_response(self) -> FilePlanWithAccounting.Response:
        return FilePlanWithAccounting.Response(
            is_plan_successfully_filed=False, plan_id=None
        )
