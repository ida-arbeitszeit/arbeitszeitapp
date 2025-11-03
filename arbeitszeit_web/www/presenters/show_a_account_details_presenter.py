from dataclasses import dataclass
from typing import List

from arbeitszeit.interactors import show_a_account_details
from arbeitszeit_web.formatters.datetime_formatter import DatetimeFormatter
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex
from arbeitszeit_web.www.navbar import NavbarItem
from arbeitszeit_web.www.presenters.transfers import TransferInfo, TransferPresenter


@dataclass
class ShowAAccountDetailsPresenter:
    @dataclass
    class ViewModel:
        transfers: List[TransferInfo]
        account_balance: str
        plot_url: str
        navbar_items: list[NavbarItem]

    translator: Translator
    url_index: UrlIndex
    datetime_formatter: DatetimeFormatter
    transfer_presenter: TransferPresenter

    def present(
        self, interactor_response: show_a_account_details.Response
    ) -> ViewModel:
        transfers = self.transfer_presenter.present_transfers(
            interactor_response.transfers
        )
        return self.ViewModel(
            transfers=transfers,
            account_balance=str(round(interactor_response.account_balance, 2)),
            plot_url=self.url_index.get_line_plot_of_company_a_account(
                interactor_response.company_id
            ),
            navbar_items=[
                NavbarItem(
                    text=self.translator.gettext("Accounts"),
                    url=self.url_index.get_company_accounts_url(
                        company_id=interactor_response.company_id
                    ),
                ),
                NavbarItem(text=self.translator.gettext("Account a"), url=None),
            ],
        )
