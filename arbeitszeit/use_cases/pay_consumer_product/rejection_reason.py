from enum import Enum, auto


class RejectionReason(Enum):
    plan_inactive = auto()
    plan_not_found = auto()
    insufficient_balance = auto()
    buyer_does_not_exist = auto()
