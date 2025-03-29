from enum import Enum, auto


class TransferType(Enum):
    credit_p = auto()
    credit_r = auto()
    credit_a = auto()
    credit_public_p = auto()
    credit_public_r = auto()
    credit_public_a = auto()
    private_consumption = auto()
    productive_consumption_p = auto()
    productive_consumption_r = auto()
    compensation_for_coop = auto()
    compensation_for_company = auto()
    work_certificates = auto()
    taxes = auto()
