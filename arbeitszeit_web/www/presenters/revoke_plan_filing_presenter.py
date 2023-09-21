from dataclasses import dataclass

from arbeitszeit.use_cases.revoke_plan_filing import RevokePlanFilingUseCase
from arbeitszeit_web.translator import Translator

from ...notification import Notifier


@dataclass
class RevokePlanFilingPresenter:
    notifier: Notifier
    translator: Translator

    def present(self, use_case_response: RevokePlanFilingUseCase.Response) -> None:
        if use_case_response.is_rejected:
            self.notifier.display_warning(
                self.translator.gettext(
                    "Unexpected error: Not possible to revoke plan filing."
                )
            )
        else:
            self.notifier.display_info(
                self.translator.gettext("Filing of plan has been successfully revoked.")
            )
