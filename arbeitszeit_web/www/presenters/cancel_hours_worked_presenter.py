from dataclasses import dataclass

from arbeitszeit.use_cases import cancel_hours_worked
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.request import Request
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class ViewModel:
    redirect_url: str


@dataclass
class CancelHoursWorkedPresenter:
    url_index: UrlIndex
    notifier: Notifier
    translator: Translator

    def render_response(
        self,
        use_case_response: cancel_hours_worked.Response,
        request: Request,
    ) -> ViewModel:

        if not use_case_response.delete_succeeded:
            self.notifier.display_warning(
                self.translator.gettext("Failed to delete registered working hours")
            )
        else:
            self.notifier.display_info(
                self.translator.gettext("Registered working hours successfully deleted")
            )
        return ViewModel(
            redirect_url=request.get_header("Referer")
            or self.url_index.get_registered_hours_worked_url()
        )
