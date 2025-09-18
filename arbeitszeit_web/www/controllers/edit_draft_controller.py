from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.interactors.edit_draft import Request as InteractorRequest
from arbeitszeit_web.forms import DraftForm
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.request import Request as WebRequest
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.www.controllers.draft_form_validator import DraftFormValidator


@dataclass
class EditDraftController:
    notifier: Notifier
    translator: Translator
    session: Session
    form_validator: DraftFormValidator

    def process_form(
        self, request: WebRequest, draft_id: UUID
    ) -> InteractorRequest | DraftForm:
        validation_result = self.form_validator.validate(request)
        if isinstance(validation_result, DraftForm):
            self.notifier.display_warning(
                self.translator.gettext("Please correct the errors in the form.")
            )
            return validation_result

        current_user = self.session.get_current_user()
        assert current_user
        return InteractorRequest(
            draft=draft_id,
            editor=current_user,
            product_name=validation_result.product_name,
            amount=validation_result.amount,
            description=validation_result.description,
            labour_cost=validation_result.labour_cost,
            means_cost=validation_result.means_cost,
            resource_cost=validation_result.resource_cost,
            is_public_service=validation_result.is_public_plan,
            timeframe=validation_result.timeframe,
            unit_of_distribution=validation_result.production_unit,
        )
