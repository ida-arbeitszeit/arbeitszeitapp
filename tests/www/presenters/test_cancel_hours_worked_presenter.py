from parameterized import parameterized

from arbeitszeit.use_cases.cancel_hours_worked import (
    Response as CancelHoursWorkedUseCaseResponse,
)
from arbeitszeit_web.www.presenters.cancel_hours_worked_presenter import (
    CancelHoursWorkedPresenter,
)
from tests.www.base_test_case import BaseTestCase


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(CancelHoursWorkedPresenter)

    def test_that_user_gets_redirected_to_registered_hours_worked(
        self,
    ) -> None:
        response = self.get_response()
        view_model = self.presenter.render_response(use_case_response=response)
        assert (
            view_model.redirect_url == self.url_index.get_registered_hours_worked_url()
        )

    @parameterized.expand(
        [
            (True,),
            (False,),
        ]
    )
    def test_for_correct_message(self, delete_succeeded) -> None:
        response = self.get_response(delete_succeeded=delete_succeeded)
        self.presenter.render_response(use_case_response=response)
        if delete_succeeded:
            assert (
                self.translator.gettext("Registered working hours successfully deleted")
                in self.notifier.infos
            )
        else:
            assert (
                self.translator.gettext("Failed to delete registered working hours")
                in self.notifier.warnings
            )

    def get_response(
        self, delete_succeeded: bool = True
    ) -> CancelHoursWorkedUseCaseResponse:
        return CancelHoursWorkedUseCaseResponse(delete_succeeded=delete_succeeded)
