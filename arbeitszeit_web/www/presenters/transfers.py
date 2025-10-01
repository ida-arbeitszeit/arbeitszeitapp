from dataclasses import dataclass

from arbeitszeit.anonymization import ANONYMIZED_STR
from arbeitszeit.services.account_details import AccountTransfer, TransferParty
from arbeitszeit.transfers import TransferType
from arbeitszeit_web.formatters.datetime_formatter import DatetimeFormatter
from arbeitszeit_web.translator import Translator


@dataclass
class TransferInfo:
    transfer_type: str
    date: str
    transfer_volume: str
    is_debit_transfer: bool
    party_name: str
    party_icon: str


@dataclass
class TransferPresenter:
    translator: Translator
    datetime_formatter: DatetimeFormatter

    def present_transfers(self, transfers: list[AccountTransfer]) -> list[TransferInfo]:
        return [self._create_info(transfer) for transfer in transfers]

    def _create_info(self, transfer: AccountTransfer) -> TransferInfo:
        return TransferInfo(
            transfer_type=description_from_transfer_type(
                self.translator, transfer.type
            ),
            date=self.datetime_formatter.format_datetime(
                date=transfer.date, fmt="%d.%m.%Y %H:%M"
            ),
            transfer_volume=str(round(transfer.volume, 2)),
            is_debit_transfer=transfer.is_debit_transfer,
            party_name=self._get_transfer_party_name(
                transfer.transfer_party, transfer.debtor_equals_creditor
            ),
            party_icon=self._get_transfer_party_type_icon(
                transfer.transfer_party, transfer.debtor_equals_creditor
            ),
        )

    def _get_transfer_party_type_icon(
        self, transfer_party: TransferParty, debtor_equals_creditor: bool
    ) -> str:
        if debtor_equals_creditor:
            return ""
        match transfer_party.type.name:
            case "member":
                return "user"
            case "company":
                return "industry"
            case "cooperation":
                return "hands-helping"
            case _:
                return ""

    def _get_transfer_party_name(
        self, transfer_party: TransferParty, debtor_equals_creditor: bool
    ) -> str:
        if debtor_equals_creditor:
            return ""
        name = transfer_party.name
        if name is ANONYMIZED_STR:
            return self.translator.gettext("Anonymous worker")
        assert isinstance(name, str)
        if name == "Social Accounting":
            name = self.translator.gettext(name)
        return name


def description_from_transfer_type(
    translator: Translator, transfer_type: TransferType
) -> str:
    match transfer_type.name:
        case "credit_p":
            return translator.gettext("Planned fixed means of production")
        case "credit_r":
            return translator.gettext("Planned liquid means of production")
        case "credit_a":
            return translator.gettext("Planned labour")
        case "credit_public_p":
            return translator.gettext(
                "Planned fixed means of production (public service)"
            )
        case "credit_public_r":
            return translator.gettext(
                "Planned liquid means of production (public service)"
            )
        case "credit_public_a":
            return translator.gettext("Planned labour (public service)")
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
