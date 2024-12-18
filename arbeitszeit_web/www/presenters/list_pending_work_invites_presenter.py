from dataclasses import dataclass

from arbeitszeit.use_cases import list_pending_work_invites
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex
from arbeitszeit_web.www.navbar import NavbarItem


@dataclass
class PendingInvite:
    member_id: str
    member_name: str


@dataclass
class ViewModel:
    pending_invites: list[PendingInvite]
    navbar_items: list[NavbarItem]


@dataclass
class ListPendingWorkInvitesPresenter:
    url_index: UrlIndex
    translator: Translator

    def present(
        self, use_case_response: list_pending_work_invites.Response
    ) -> ViewModel:
        return ViewModel(
            pending_invites=[
                PendingInvite(
                    member_id=str(invite.member_id), member_name=invite.member_name
                )
                for invite in use_case_response.pending_invites
            ],
            navbar_items=[
                NavbarItem(
                    text=self.translator.gettext("Workers"),
                    url=self.url_index.get_invite_worker_to_company_url(),
                ),
                NavbarItem(
                    text=self.translator.gettext("Pending work invites"), url=None
                ),
            ],
        )
