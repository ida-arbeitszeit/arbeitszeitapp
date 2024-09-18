from parameterized import parameterized

from arbeitszeit.use_cases.register_private_consumption import (
    RegisterPrivateConsumptionResponse,
    RejectionReason,
)
from arbeitszeit_web.www.presenters.register_private_consumption_presenter import (
    Redirect,
    RegisterPrivateConsumptionPresenter,
    RenderForm,
)
from tests.request import FakeRequest
from tests.www.base_test_case import BaseTestCase


class RegisterPrivateConsumptionPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(RegisterPrivateConsumptionPresenter)

    def test_presenter_shows_correct_notification_when_registration_was_a_success(
        self,
    ) -> None:
        self.presenter.present(
            RegisterPrivateConsumptionResponse(rejection_reason=None),
            request=FakeRequest(),
        )
        self.assertIn(
            self.translator.gettext("Consumption successfully registered."),
            self.notifier.infos,
        )

    def test_presenter_shows_correct_notification_when_plan_was_inactive(self) -> None:
        view_model = self.presenter.present(
            RegisterPrivateConsumptionResponse(
                rejection_reason=RejectionReason.plan_inactive
            ),
            request=FakeRequest(),
        )
        assert isinstance(view_model, RenderForm)
        assert (
            self.translator.gettext(
                "The specified plan has been expired. Please contact the selling company to provide you with an up-to-date plan ID."
            )
            in view_model.form.plan_id_errors
        )

    def test_presenter_shows_correct_notification_when_plan_was_not_found(self) -> None:
        view_model = self.presenter.present(
            RegisterPrivateConsumptionResponse(
                rejection_reason=RejectionReason.plan_not_found
            ),
            request=FakeRequest(),
        )
        assert isinstance(view_model, RenderForm)
        assert (
            self.translator.gettext(
                "There is no plan with the specified ID in the database."
            )
            in view_model.form.plan_id_errors
        )

    def test_presenter_shows_correct_notification_when_member_has_insufficient_balance(
        self,
    ) -> None:
        view_model = self.presenter.present(
            RegisterPrivateConsumptionResponse(
                rejection_reason=RejectionReason.insufficient_balance
            ),
            request=FakeRequest(),
        )
        assert isinstance(view_model, RenderForm)
        assert (
            self.translator.gettext("You do not have enough work certificates.")
            in view_model.form.general_errors
        )

    def test_presenter_returns_404_status_code_when_plan_was_not_found(self) -> None:
        view_model = self.presenter.present(
            RegisterPrivateConsumptionResponse(
                rejection_reason=RejectionReason.plan_not_found
            ),
            request=FakeRequest(),
        )
        assert isinstance(view_model, RenderForm)
        self.assertEqual(view_model.status_code, 404)

    def test_that_presenter_returns_a_redirect_when_registration_was_successful(
        self,
    ) -> None:
        view_model = self.presenter.present(
            RegisterPrivateConsumptionResponse(rejection_reason=None),
            request=FakeRequest(),
        )
        assert isinstance(view_model, Redirect)

    def test_that_user_is_redirected_to_register_private_consumption_view_on_successful_registration(
        self,
    ) -> None:
        view_model = self.presenter.present(
            RegisterPrivateConsumptionResponse(rejection_reason=None),
            request=FakeRequest(),
        )
        assert isinstance(view_model, Redirect)
        assert view_model.url == self.url_index.get_register_private_consumption_url()

    @parameterized.expand([(reason,) for reason in RejectionReason])
    def test_that_error_response_results_in_form_being_rerendered(
        self, reason: RejectionReason
    ) -> None:
        view_model = self.presenter.present(
            RegisterPrivateConsumptionResponse(rejection_reason=reason),
            request=FakeRequest(),
        )
        assert isinstance(view_model, RenderForm)

    def test_presenter_returns_410_status_code_when_plan_is_inactive(self) -> None:
        view_model = self.presenter.present(
            RegisterPrivateConsumptionResponse(
                rejection_reason=RejectionReason.plan_inactive
            ),
            request=FakeRequest(),
        )
        assert isinstance(view_model, RenderForm)
        self.assertEqual(view_model.status_code, 410)

    def test_presenter_returns_406_status_code_when_member_has_insufficient_balance(
        self,
    ) -> None:
        view_model = self.presenter.present(
            RegisterPrivateConsumptionResponse(
                rejection_reason=RejectionReason.insufficient_balance
            ),
            request=FakeRequest(),
        )
        assert isinstance(view_model, RenderForm)
        self.assertEqual(view_model.status_code, 406)

    def test_for_proper_error_message_if_user_does_not_exist(
        self,
    ) -> None:
        view_model = self.presenter.present(
            RegisterPrivateConsumptionResponse(
                rejection_reason=RejectionReason.consumer_does_not_exist
            ),
            request=FakeRequest(),
        )
        assert isinstance(view_model, RenderForm)
        assert (
            self.translator.gettext(
                "Failed to register private consumption. Are you logged in as a member?"
            )
            in view_model.form.general_errors
        )

    def test_presenter_returns_404_status_code_when_consumer_does_not_exist(
        self,
    ) -> None:
        view_model = self.presenter.present(
            RegisterPrivateConsumptionResponse(
                rejection_reason=RejectionReason.consumer_does_not_exist
            ),
            request=FakeRequest(),
        )
        assert isinstance(view_model, RenderForm)
        self.assertEqual(view_model.status_code, 404)
