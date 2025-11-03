from dataclasses import dataclass

from arbeitszeit.interactors.get_member_account import GetMemberAccountResponse
from arbeitszeit_web.formatters.datetime_formatter import DatetimeFormatter
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.www.presenters.transfers import TransferInfo, TransferPresenter


@dataclass
class GetMemberAccountPresenter:
    @dataclass
    class ViewModel:
        balance: str
        is_balance_positive: bool
        transfers: list[TransferInfo]

    datetime_formatter: DatetimeFormatter
    translator: Translator
    transfer_presenter: TransferPresenter

    def present_member_account(
        self, interactor_response: GetMemberAccountResponse
    ) -> ViewModel:
        transfers = self.transfer_presenter.present_transfers(
            interactor_response.transfers
        )
        return self.ViewModel(
            balance=f"{round(interactor_response.balance, 2)}",
            is_balance_positive=interactor_response.balance >= 0,
            transfers=transfers,
        )
