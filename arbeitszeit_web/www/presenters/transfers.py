from dataclasses import dataclass

from arbeitszeit.services.account_details import AccountTransfer
from arbeitszeit.transfers import TransferType
from arbeitszeit_web.formatters.datetime_formatter import DatetimeFormatter
from arbeitszeit_web.translator import Translator


@dataclass
class TransferInfo:
    transfer_type: str
    date: str
    transfer_volume: str
    is_debit_transfer: bool


@dataclass
class TransferPresenter:
    translator: Translator
    datetime_formatter: DatetimeFormatter

    def present_transfers(self, transfers: list[AccountTransfer]) -> list[TransferInfo]:
        return [self._create_info(transfer) for transfer in transfers]

    def _create_info(self, transfer: AccountTransfer) -> TransferInfo:
        return TransferInfo(
            transfer_type=transfer_description_from_transfer_type(
                self.translator, transfer.type
            ),
            date=self.datetime_formatter.format_datetime(
                date=transfer.date, fmt="%d.%m.%Y %H:%M"
            ),
            transfer_volume=str(round(transfer.volume, 2)),
            is_debit_transfer=transfer.is_debit_transfer,
        )


def transfer_description_from_transfer_type(
    translator: Translator, transfer_type: TransferType
) -> str:
    match transfer_type.name:
        case "credit_p":
            return translator.gettext("Credit for fixed means of production")
        case "credit_r":
            return translator.gettext("Credit for liquid means of production")
        case "credit_a":
            return translator.gettext("Credit for labour")
        case "credit_public_p":
            return translator.gettext(
                "Credit for fixed means of production (public service)"
            )
        case "credit_public_r":
            return translator.gettext(
                "Credit for liquid means of production (public service)"
            )
        case "credit_public_a":
            return translator.gettext("Credit for labour (public service)")
        case "private_consumption":
            return translator.gettext("Private consumption")
        case "productive_consumption_p":
            return translator.gettext(
                "Productive consumption of fixed means of production"
            )
        case "productive_consumption_r":
            return translator.gettext(
                "Productive consumption of liquid means of production"
            )
        case "compensation_for_coop":
            return translator.gettext("Compensation for overproductive planning")
        case "compensation_for_company":
            return translator.gettext("Compensation for underproductive planning")
        case "work_certificates":
            return translator.gettext("Work certificates")
        case "taxes":
            return translator.gettext("Contribution to public sector")
        case _:
            raise ValueError(f"Unknown transfer type: {transfer_type}")
