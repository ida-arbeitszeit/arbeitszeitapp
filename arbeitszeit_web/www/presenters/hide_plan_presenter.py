from dataclasses import dataclass

from arbeitszeit.use_cases.hide_plan import HidePlanResponse
from arbeitszeit_web.translator import Translator

from ...notification import Notifier


@dataclass
class HidePlanPresenter:
    notifier: Notifier
    trans: Translator

    def present(self, use_case_response: HidePlanResponse) -> None:
        if use_case_response.is_success:
            self.notifier.display_info(
                self.trans.gettext(
                    "Expired plan %(plan_id)s is no longer shown to you."
                )
                % dict(plan_id=use_case_response.plan_id)
            )
