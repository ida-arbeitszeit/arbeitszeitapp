from dataclasses import dataclass

from arbeitszeit.interactors.file_plan_with_accounting import FilePlanWithAccounting
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex, UserUrlIndex


@dataclass
class FilePlanWithAccountingPresenter:
    @dataclass
    class ViewModel:
        redirect_url: str

    user_url_index: UserUrlIndex
    url_index: UrlIndex
    notifier: Notifier
    translator: Translator

    def present_response(self, response: FilePlanWithAccounting.Response) -> ViewModel:
        plan_id = response.plan_id
        if plan_id is not None and response.is_plan_successfully_filed:
            redirect_url = self.user_url_index.get_plan_details_url(plan_id)
            self.notifier.display_info(
                self.translator.gettext(
                    "Successfully filed plan with social accounting"
                )
            )
        else:
            redirect_url = self.url_index.get_my_plans_url()
            self.notifier.display_warning(
                self.translator.gettext("Could not file plan with social accounting")
            )
        return self.ViewModel(redirect_url=redirect_url)
