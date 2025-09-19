from dataclasses import dataclass

from arbeitszeit.interactors.revoke_plan_filing import RevokePlanFilingInteractor
from arbeitszeit_web.translator import Translator

from ...notification import Notifier


@dataclass
class RevokePlanFilingPresenter:
    notifier: Notifier
    translator: Translator

    def present(self, interactor_response: RevokePlanFilingInteractor.Response) -> None:
        if interactor_response.is_rejected:
            self.notifier.display_warning(
                self.translator.gettext(
                    "Unexpected error: Not possible to revoke plan filing."
                )
            )
        else:
            self.notifier.display_info(
                self.translator.gettext("Filing of plan has been successfully revoked.")
            )
