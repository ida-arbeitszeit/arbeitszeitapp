from dataclasses import dataclass
from typing import Dict, Union

from injector import inject

from arbeitszeit.entities import Company, Member, SocialAccounting, Transaction
from arbeitszeit.repositories import (
    AccountOwnerRepository,
    MemberRepository,
    TransactionRepository,
)


@inject
@dataclass
class GetTransactionInfos:
    transaction_repository: TransactionRepository
    member_repository: MemberRepository
    acount_owner_repository: AccountOwnerRepository

    def __call__(self, transaction: Transaction) -> Dict:
        """
        This function returns transaction information:
        - transaction: Transaction
        - sender: Union[Member, Company]
        - receiver: Union[Member, Company]
        """

        trans_info: Dict = {}
        sender: Union[Member, Company, SocialAccounting]
        receiver: Union[Member, Company, SocialAccounting]

        sending_account = transaction.account_from
        sender = self.acount_owner_repository.get_account_owner(sending_account)

        receiving_account = transaction.account_to
        receiver = self.acount_owner_repository.get_account_owner(receiving_account)

        trans_info["transaction"] = transaction
        trans_info["sender"] = sender
        trans_info["receiver"] = receiver

        return trans_info
