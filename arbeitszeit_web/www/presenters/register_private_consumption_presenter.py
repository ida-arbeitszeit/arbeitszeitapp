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
class RenderForm:
    status_code: int
    form: RegisterPrivateConsumptionForm


@dataclass
class Redirect:
    url: str


RegisterPrivateConsumptionViewModel = Redirect | RenderForm


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
        if use_case_response.rejection_reason is None:
            self.user_notifier.display_info(
                self.translator.gettext("Consumption successfully registered.")
            )
            return Redirect(url=self.url_index.get_register_private_consumption_url())
        form = self._create_form(request)
        status_code = 400
        if use_case_response.rejection_reason == RejectionReason.plan_inactive:
            form.plan_id_errors.append(
                self.translator.gettext(
                    "The specified plan has been expired. Please contact the selling company to provide you with an up-to-date plan ID."
                )
            )
            status_code = 410
        elif use_case_response.rejection_reason == RejectionReason.insufficient_balance:
            form.general_errors.append(
                self.translator.gettext("You do not have enough work certificates.")
            )
            status_code = 406
        elif (
            use_case_response.rejection_reason
            == RejectionReason.consumer_does_not_exist
        ):
            form.general_errors.append(
                self.translator.gettext(
                    "Failed to register private consumption. Are you logged in as a member?"
                )
            )
            status_code = 404
        else:
            form.plan_id_errors.append(
                self.translator.gettext(
                    "There is no plan with the specified ID in the database."
                )
            )
            status_code = 404
        return RenderForm(status_code=status_code, form=form)

    def _create_form(self, request: Request) -> RegisterPrivateConsumptionForm:
        return RegisterPrivateConsumptionForm(
            plan_id_value=request.get_form("plan_id") or "",
            amount_value=request.get_form("amount") or "",
        )
