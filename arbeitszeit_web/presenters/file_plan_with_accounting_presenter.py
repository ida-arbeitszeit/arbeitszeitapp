from dataclasses import dataclass
from typing import Optional

from arbeitszeit.use_cases.file_plan_with_accounting import FilePlanWithAccounting
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import PlanSummaryUrlIndex


@dataclass
class FilePlanWithAccountingPresenter:
    @dataclass
    class ViewModel:
        redirect_url: Optional[str]

    plan_summary_url_index: PlanSummaryUrlIndex
    notifier: Notifier
    translator: Translator

    def present_response(self, response: FilePlanWithAccounting.Response) -> ViewModel:
        plan_id = response.plan_id
        if plan_id is not None and response.is_plan_successfully_filed:
            redirect_url = self.plan_summary_url_index.get_plan_summary_url(plan_id)
            self.notifier.display_info(
                self.translator.gettext(
                    "Successfully filed plan with social accounting"
                )
            )
        else:
            redirect_url = None
            self.notifier.display_warning(
                self.translator.gettext("Could not file plan with social accounting")
            )
        return self.ViewModel(redirect_url=redirect_url)
