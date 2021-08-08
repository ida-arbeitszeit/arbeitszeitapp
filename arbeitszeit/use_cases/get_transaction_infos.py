from dataclasses import dataclass
from itertools import chain
from typing import List, Union

from injector import inject

from arbeitszeit.entities import Company, Member, SocialAccounting
from arbeitszeit.repositories import (
    AccountOwnerRepository,
    MemberRepository,
    TransactionRepository,
)


def _create_member_info(
    transaction,
    sender,
    receiver,
    user_is_sender,
    user_is_receiver,
):
    """this helper function creates transaction info for members."""
    # sender_name
    if user_is_sender:
        sender_name = "Mir"
    elif isinstance(sender, Company) or isinstance(sender, Member):
        sender_name = sender.name

    # receiver_name
    if user_is_receiver:
        receiver_name = "Mich"
    elif isinstance(receiver, Company) or isinstance(receiver, Member):
        receiver_name = receiver.name

    # amount
    if user_is_sender:
        amount = -transaction.amount
    elif user_is_receiver:
        amount = transaction.amount

    info = [transaction.date, sender_name, receiver_name, amount, transaction.purpose]
    return info


def _create_company_info(
    user,
    transaction,
    sender,
    sending_account,
    receiver,
    receiving_account,
    user_is_sender,
    user_is_receiver,
):
    """this helper function creates transaction info for companies."""
    # sender_name
    if user_is_sender:
        sender_name = "Mir"
    elif isinstance(sender, Company) or isinstance(sender, Member):
        sender_name = sender.name
    elif isinstance(sender, SocialAccounting):
        sender_name = "Öff. Buchhaltung"

    # receiver_name
    if user_is_receiver:
        receiver_name = "Mich"
    elif isinstance(receiver, Company) or isinstance(receiver, Member):
        receiver_name = receiver.name

    # change_p/r/a/prd
    if user_is_sender and user_is_receiver:  # company buys from itself
        change_p = (
            -1 * transaction.amount if sending_account == user.means_account else ""
        )
        change_r = (
            -1 * transaction.amount
            if sending_account == user.raw_material_account
            else ""
        )
        change_a = (
            -1 * transaction.amount if sending_account == user.work_account else ""
        )
        change_prd = (
            1 * transaction.amount if receiving_account == user.product_account else ""
        )

    elif user_is_sender:
        factor = -1

        change_p = (
            factor * transaction.amount if sending_account == user.means_account else ""
        )
        change_r = (
            factor * transaction.amount
            if sending_account == user.raw_material_account
            else ""
        )
        change_a = (
            factor * transaction.amount if sending_account == user.work_account else ""
        )
        change_prd = (
            factor * transaction.amount
            if sending_account == user.product_account
            else ""
        )

    elif user_is_receiver:
        factor = 1

        change_p = (
            factor * transaction.amount
            if receiving_account == user.means_account
            else ""
        )
        change_r = (
            factor * transaction.amount
            if receiving_account == user.raw_material_account
            else ""
        )
        change_a = (
            factor * transaction.amount
            if receiving_account == user.work_account
            else ""
        )
        change_prd = (
            factor * transaction.amount
            if receiving_account == user.product_account
            else ""
        )

    info = [
        transaction.date,
        sender_name,
        receiver_name,
        change_p,
        change_r,
        change_a,
        change_prd,
        transaction.purpose,
    ]
    return info


@inject
@dataclass
class GetTransactionInfos:
    transaction_repository: TransactionRepository
    member_repository: MemberRepository
    acount_owner_repository: AccountOwnerRepository

    def __call__(self, user: Union[Member, Company]) -> List[List]:
        """
        This function returns a user's transaction information.
        """

        sender: Union[Member, Company, SocialAccounting]
        receiver: Union[Member, Company, SocialAccounting]
        user_is_sender: bool = False
        user_is_receiver: bool = False

        if isinstance(user, Company):
            # get all transactions where company is involved in
            all_transactions = list(
                chain(
                    self.transaction_repository.all_transactions_sent_by_account(
                        user.means_account
                    ),
                    self.transaction_repository.all_transactions_sent_by_account(
                        user.raw_material_account
                    ),
                    self.transaction_repository.all_transactions_sent_by_account(
                        user.work_account
                    ),
                    self.transaction_repository.all_transactions_sent_by_account(
                        user.product_account
                    ),
                    self.transaction_repository.all_transactions_received_by_account(
                        user.means_account
                    ),
                    self.transaction_repository.all_transactions_received_by_account(
                        user.raw_material_account
                    ),
                    self.transaction_repository.all_transactions_received_by_account(
                        user.work_account
                    ),
                    self.transaction_repository.all_transactions_received_by_account(
                        user.product_account
                    ),
                )
            )

            # sort transactions
            all_transactions_sorted = sorted(
                all_transactions, key=lambda x: x.date, reverse=True
            )

            # get infos on every transaction company is involved in
            all_trans_infos = []
            for transaction in all_transactions_sorted:
                sending_account = transaction.account_from
                # defining sender
                if sending_account in [
                    user.means_account,
                    user.raw_material_account,
                    user.work_account,
                    user.product_account,
                ]:
                    sender = user
                    user_is_sender = True
                else:
                    sender = self.acount_owner_repository.get_account_owner(
                        sending_account
                    )

                # defining receiver
                receiving_account = transaction.account_to
                if receiving_account in [
                    user.means_account,
                    user.raw_material_account,
                    user.work_account,
                    user.product_account,
                ]:
                    receiver = user
                    user_is_receiver = True
                else:
                    receiver = self.acount_owner_repository.get_account_owner(
                        receiving_account
                    )

                info = _create_company_info(
                    user,
                    transaction,
                    sender,
                    sending_account,
                    receiver,
                    receiving_account,
                    user_is_sender,
                    user_is_receiver,
                )
                all_trans_infos.append(info)

        elif isinstance(user, Member):
            all_transactions = list(
                chain(
                    self.transaction_repository.all_transactions_sent_by_account(
                        user.account
                    ),
                    self.transaction_repository.all_transactions_received_by_account(
                        user.account
                    ),
                )
            )
            all_transactions_sorted = sorted(
                all_transactions, key=lambda x: x.date, reverse=True
            )

            all_trans_infos = []
            for transaction in all_transactions_sorted:
                sending_account = transaction.account_from
                # defining sender
                if sending_account == user.account:
                    sender = user
                    user_is_sender = True
                else:
                    sender = self.acount_owner_repository.get_account_owner(
                        sending_account
                    )

                receiving_account = transaction.account_to
                # defining receiver
                if receiving_account == user.account:
                    receiver = user
                    user_is_receiver = True
                else:
                    receiver = self.acount_owner_repository.get_account_owner(
                        receiving_account
                    )

                info = _create_member_info(
                    transaction,
                    sender,
                    receiver,
                    user_is_sender,
                    user_is_receiver,
                )

                all_trans_infos.append(info)

        if all_transactions:
            assert (
                user_is_sender or user_is_receiver
            ), "User is neither sender nor receiver of the transaction"
        return all_trans_infos
