from parameterized import parameterized

from arbeitszeit.use_cases.cancel_hours_worked import (
    Response as CancelHoursWorkedUseCaseResponse,
)
from arbeitszeit_web.www.presenters.cancel_hours_worked_presenter import (
    CancelHoursWorkedPresenter,
)
from tests.request import FakeRequest
from tests.www.base_test_case import BaseTestCase


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(CancelHoursWorkedPresenter)

    def test_that_user_gets_redirected_to_registered_hours_worked_via_referer_header(
        self,
    ) -> None:
        expectedRedirectUrl = "/list_registered_hours_worked"
        request = FakeRequest()
        request.set_header(key="Referer", value=expectedRedirectUrl)
        response = self.get_response()
        view_model = self.presenter.render_response(
            use_case_response=response, request=request
        )
        self.assertEqual(view_model.redirect_url, expectedRedirectUrl)

    def test_that_user_gets_redirected_to_registered_hours_worked_via_url_index(
        self,
    ) -> None:
        expectedRedirectUrlIndex = "/get_registered_hours_worked_url"
        request = FakeRequest()
        request.set_header(key="Referer", value="")
        response = self.get_response()
        view_model = self.presenter.render_response(
            use_case_response=response, request=request
        )
        self.assertIn(expectedRedirectUrlIndex, view_model.redirect_url)

    @parameterized.expand(
        [
            (True,),
            (False,),
        ]
    )
    def test_for_correct_message(self, delete_succeeded) -> None:
        request = FakeRequest()
        response = self.get_response(delete_succeeded=delete_succeeded)
        self.presenter.render_response(use_case_response=response, request=request)
        if delete_succeeded:
            self.assertIn(
                self.translator.gettext(
                    "Registered working hours successfully deleted"
                ),
                self.notifier.infos,
            )
        else:
            self.assertIn(
                self.translator.gettext("Failed to delete registered working hours"),
                self.notifier.warnings,
            )

    def get_response(
        self, delete_succeeded: bool = True
    ) -> CancelHoursWorkedUseCaseResponse:
        return CancelHoursWorkedUseCaseResponse(delete_succeeded=delete_succeeded)
