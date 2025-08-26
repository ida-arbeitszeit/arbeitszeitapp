from __future__ import annotations

from dataclasses import dataclass
from typing import List

from arbeitszeit.transfers import TransferType
from arbeitszeit.use_cases.get_member_account import GetMemberAccountResponse
from arbeitszeit_web.formatters.datetime_formatter import DatetimeFormatter
from arbeitszeit_web.translator import Translator


@dataclass
class GetMemberAccountPresenter:
    @dataclass
    class Transfer:
        date: str
        type: str
        user_name: str
        volume: str
        is_volume_positive: bool

    @dataclass
    class ViewModel:
        balance: str
        is_balance_positive: bool
        transfers: List[GetMemberAccountPresenter.Transfer]

    datetime_formatter: DatetimeFormatter
    translator: Translator

    def present_member_account(
        self, use_case_response: GetMemberAccountResponse
    ) -> ViewModel:
        transfers = [
            self.Transfer(
                date=self.datetime_formatter.format_datetime(
                    t.date, zone="Europe/Berlin", fmt="%d.%m.%Y %H:%M"
                ),
                type=self._transfer_type_as_string(t.type),
                user_name=t.peer_name,
                volume=f"{round(t.transferred_value, 2)}",
                is_volume_positive=t.transferred_value >= 0,
            )
            for t in use_case_response.transfers
        ]
        return self.ViewModel(
            balance=f"{round(use_case_response.balance, 2)}",
            is_balance_positive=use_case_response.balance >= 0,
            transfers=transfers,
        )

    def _transfer_type_as_string(self, t: TransferType) -> str:
        if t == TransferType.work_certificates:
            return self.translator.gettext("Work certificates")
        elif t == TransferType.taxes:
            return self.translator.gettext("Contribution to public sector")
        else:
            return self.translator.gettext("Consumption")
