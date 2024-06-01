from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.use_cases.edit_draft import Request
from arbeitszeit_web.forms import DraftForm
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator


@dataclass
class EditDraftController:
    notifier: Notifier
    translator: Translator
    session: Session

    def process_form(self, form: DraftForm, draft_id: UUID) -> Request | None:
        product_name = form.product_name_field().get_value()
        if not product_name:
            form.product_name_field().attach_error(
                self.translator.gettext("The product name field cannot be empty.")
            )
            return None
        description = form.description_field().get_value()
        if not description:
            form.description_field().attach_error(
                self.translator.gettext("The description field cannot be empty.")
            )
            return None
        unit_of_distribution = form.unit_of_distribution_field().get_value()
        if not unit_of_distribution:
            form.unit_of_distribution_field().attach_error(
                self.translator.gettext(
                    "The smallest delivery unit field cannot be empty."
                )
            )
            return None
        labour_cost = form.labour_cost_field().get_value()
        means_cost = form.means_cost_field().get_value()
        resource_cost = form.resource_cost_field().get_value()
        if not (labour_cost or means_cost or resource_cost):
            self.notifier.display_warning(
                self.translator.gettext(
                    "At least one of the costs fields must be a positive number of hours."
                )
            )
            return None
        amount = form.amount_field().get_value()
        if amount == 0:
            form.amount_field().attach_error(
                self.translator.gettext("The product amount planned cannot be 0.")
            )
            return None
        elif amount < 0:
            form.amount_field().attach_error(
                self.translator.gettext(
                    "The planned product amount cannot be negative."
                )
            )
            return None
        timeframe = form.timeframe_field().get_value()
        if timeframe == 0:
            form.timeframe_field().attach_error(
                self.translator.gettext("The planning timeframe cannot be 0 days.")
            )
            return None
        elif timeframe < 0:
            form.timeframe_field().attach_error(
                self.translator.gettext(
                    "The planning timeframe cannot be a negative number of days."
                )
            )
            return None
        current_user = self.session.get_current_user()
        if current_user is None:
            return None
        return Request(
            draft=draft_id,
            editor=current_user,
            product_name=product_name,
            amount=amount,
            description=description,
            labour_cost=labour_cost,
            means_cost=means_cost,
            resource_cost=resource_cost,
            is_public_service=form.is_public_service_field().get_value(),
            timeframe=timeframe,
            unit_of_distribution=unit_of_distribution,
        )
