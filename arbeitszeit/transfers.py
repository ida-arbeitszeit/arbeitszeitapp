from enum import Enum


class TransferType(Enum):
    """
    See https://workers-control.readthedocs.io/en/latest/concepts.html for
    a documentation of the transfer types.
    """

    credit_p = "credit_p"
    credit_r = "credit_r"
    credit_a = "credit_a"
    credit_public_p = "credit_public_p"
    credit_public_r = "credit_public_r"
    credit_public_a = "credit_public_a"
    private_consumption = "private_consumption"
    productive_consumption_p = "productive_consumption_p"
    productive_consumption_r = "productive_consumption_r"
    compensation_for_coop = "compensation_for_coop"
    compensation_for_company = "compensation_for_company"
    work_certificates = "work_certificates"
    taxes = "taxes"
