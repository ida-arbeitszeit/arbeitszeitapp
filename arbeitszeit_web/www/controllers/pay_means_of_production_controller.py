from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.records import PurposesOfPurchases
from arbeitszeit.use_cases.pay_means_of_production import PayMeansOfProductionRequest
from arbeitszeit_web.forms import PayMeansOfProductionForm
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator


@dataclass
class PayMeansOfProductionController:
    class FormError(Exception):
        pass

    session: Session
    translator: Translator

    def process_input_data(
        self, form: PayMeansOfProductionForm
    ) -> PayMeansOfProductionRequest:
        buyer = self.session.get_current_user()
        assert buyer
        try:
            plan = UUID(form.plan_id_field().get_value().strip())
        except ValueError:
            form.plan_id_field().attach_error(self.translator.gettext("Invalid ID."))
            raise self.FormError()
        try:
            amount = int(form.amount_field().get_value())
        except ValueError:
            form.amount_field().attach_error(
                self.translator.gettext("This is not an integer.")
            )
            raise self.FormError()
        if amount <= 0:
            form.amount_field().attach_error(
                self.translator.gettext("Must be a number larger than zero.")
            )
            raise self.FormError()
        type_of_payment = form.type_of_payment_field().get_value()
        if not type_of_payment:
            form.type_of_payment_field().attach_error(
                self.translator.gettext("This field is required.")
            )
            raise self.FormError()
        purpose = (
            PurposesOfPurchases.means_of_prod
            if type_of_payment == "fixed"
            else PurposesOfPurchases.raw_materials
        )
        return PayMeansOfProductionRequest(buyer, plan, amount, purpose)
