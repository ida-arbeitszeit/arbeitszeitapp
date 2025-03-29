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
    class Transaction:
        date: str
        type: str
        user_name: str
        volume: str
        is_volume_positive: bool
        purpose: str

    @dataclass
    class ViewModel:
        balance: str
        is_balance_positive: bool
        transactions: List[GetMemberAccountPresenter.Transaction]

    datetime_formatter: DatetimeFormatter
    translator: Translator

    def present_member_account(
        self, use_case_response: GetMemberAccountResponse
    ) -> ViewModel:
        transactions = [
            self.Transaction(
                date=self.datetime_formatter.format_datetime(
                    t.date, zone="Europe/Berlin", fmt="%d.%m.%Y %H:%M"
                ),
                type=self._transfer_type_as_string(t.type),
                user_name=t.peer_name,
                volume=f"{round(t.transaction_volume, 2)}",
                is_volume_positive=t.transaction_volume >= 0,
                purpose="" if t.type == TransferType.work_certificates else t.purpose,
            )
            for t in use_case_response.transactions
        ]
        return self.ViewModel(
            balance=f"{round(use_case_response.balance, 2)}",
            is_balance_positive=use_case_response.balance >= 0,
            transactions=transactions,
        )

    def _transfer_type_as_string(self, t: TransferType) -> str:
        if t == TransferType.work_certificates:
            return self.translator.gettext("Work certificates")
        elif t == TransferType.taxes:
            return self.translator.gettext("Contribution to public sector")
        else:
            return self.translator.gettext("Consumption")
