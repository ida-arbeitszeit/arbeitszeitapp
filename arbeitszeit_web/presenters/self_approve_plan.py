from dataclasses import dataclass

from arbeitszeit.use_cases.self_approve_plan import SelfApprovePlan
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.translator import Translator


@dataclass
class SelfApprovePlanPresenter:
    @dataclass
    class ViewModel:
        pass

    notifier: Notifier
    translator: Translator

    def present_response(self, response: SelfApprovePlan.Response) -> ViewModel:
        if response.is_approved:
            self.notifier.display_info(
                self.translator.gettext("Plan was successfully created and approved.")
            )
            self.notifier.display_info(
                self.translator.gettext(
                    "Plan was activated. Credit for means of production were granted. Certificates for labour will be transferred daily"
                )
            )
        else:
            self.notifier.display_warning(
                self.translator.gettext("Plan not approved. Reason: %(reason)s")
                % dict(reason=response.reason)
            )
        return self.ViewModel()
