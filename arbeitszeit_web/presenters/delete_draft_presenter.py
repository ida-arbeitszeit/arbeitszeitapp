from dataclasses import dataclass

from injector import inject

from arbeitszeit.use_cases.delete_draft import DeleteDraftUseCase
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.session import Session
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@inject
@dataclass
class DeleteDraftPresenter:
    url_index: UrlIndex
    notifier: Notifier
    translator: Translator
    session: Session

    @dataclass
    class ViewModel:
        redirect_target: str

    def present_draft_deletion(
        self, response: DeleteDraftUseCase.Response
    ) -> ViewModel:
        self.notifier.display_info(
            self.translator.gettext(
                "Plan draft %(product_name)s was deleted"
                % dict(product_name=response.product_name)
            )
        )
        return self.ViewModel(
            redirect_target=self.session.pop_next_url()
            or self.url_index.get_draft_list_url()
        )
