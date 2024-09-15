from dataclasses import dataclass

from arbeitszeit.use_cases.register_private_consumption import (
    RegisterPrivateConsumptionResponse,
    RejectionReason,
)
from arbeitszeit_web.forms import RegisterPrivateConsumptionForm
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.request import Request
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class RegisterPrivateConsumptionViewModel:
    status_code: int | None
    form: RegisterPrivateConsumptionForm
    redirect_url: str | None = None


@dataclass
class RegisterPrivateConsumptionPresenter:
    user_notifier: Notifier
    translator: Translator
    url_index: UrlIndex

    def present(
        self,
        use_case_response: RegisterPrivateConsumptionResponse,
        request: Request,
    ) -> RegisterPrivateConsumptionViewModel:
        form = RegisterPrivateConsumptionForm(
            plan_id_value="",
            amount_value="",
        )
        if use_case_response.rejection_reason is None:
            self.user_notifier.display_info(
                self.translator.gettext("Consumption successfully registered.")
            )
            return RegisterPrivateConsumptionViewModel(
                status_code=None,
                form=form,
                redirect_url=self.url_index.get_register_private_consumption_url(),
            )
        elif use_case_response.rejection_reason == RejectionReason.plan_inactive:
            self.user_notifier.display_warning(
                self.translator.gettext(
                    "The specified plan has been expired. Please contact the selling company to provide you with an up-to-date plan ID."
                )
            )
            return RegisterPrivateConsumptionViewModel(status_code=410, form=form)
        elif use_case_response.rejection_reason == RejectionReason.insufficient_balance:
            self.user_notifier.display_warning(
                self.translator.gettext("You do not have enough work certificates.")
            )
            return RegisterPrivateConsumptionViewModel(status_code=406, form=form)
        elif (
            use_case_response.rejection_reason
            == RejectionReason.consumer_does_not_exist
        ):
            self.user_notifier.display_warning(
                self.translator.gettext(
                    "Failed to register private consumption. Are you logged in as a member?"
                )
            )
            return RegisterPrivateConsumptionViewModel(status_code=404, form=form)
        else:
            self.user_notifier.display_warning(
                self.translator.gettext(
                    "There is no plan with the specified ID in the database."
                )
            )
            return RegisterPrivateConsumptionViewModel(
                status_code=404, form=form, redirect_url=None
            )
