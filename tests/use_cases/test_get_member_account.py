from datetime import timedelta
from decimal import Decimal

from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.get_member_account import GetMemberAccount
from tests.data_generators import (
    CompanyGenerator,
    FakeDatetimeService,
    MemberGenerator,
    TransactionGenerator,
)

from .dependency_injection import injection_test


@injection_test
def test_that_balance_is_zero_when_no_transaction_took_place(
    use_case: GetMemberAccount,
    member_generator: MemberGenerator,
):
    member = member_generator.create_member()
    response = use_case(member)
    assert response.balance == 0


@injection_test
def test_that_transactions_is_empty_when_no_transaction_took_place(
    use_case: GetMemberAccount,
    member_generator: MemberGenerator,
):
    member = member_generator.create_member()
    response = use_case(member)
    assert not response.transactions


@injection_test
def test_that_transactions_is_empty_when_member_is_not_involved_in_transaction(
    use_case: GetMemberAccount,
    member_generator: MemberGenerator,
    transaction_generator: TransactionGenerator,
    company_generator: CompanyGenerator,
):
    member_of_interest = member_generator.create_member()
    company = company_generator.create_company_entity()
    other_member = member_generator.create_member_entity()

    transaction_generator.create_transaction(
        sending_account=other_member.account,
        receiving_account=company.product_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(8.5),
    )

    response = use_case(member_of_interest)
    assert not response.transactions


@injection_test
def test_that_correct_info_is_generated_after_member_pays_product(
    use_case: GetMemberAccount,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    member = member_generator.create_member_entity()
    company = company_generator.create_company_entity()

    transaction_generator.create_transaction(
        sending_account=member.account,
        receiving_account=company.product_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(8.5),
    )

    response = use_case(member.id)
    assert len(response.transactions) == 1
    assert response.transactions[0].peer_name == company.name
    assert response.transactions[0].transaction_volume == Decimal(-10)
    assert response.transactions[0].type == TransactionTypes.payment_of_consumer_product
    assert response.balance == Decimal(-10)


@injection_test
def test_that_a_transaction_with_volume_zero_is_shown_correctly(
    use_case: GetMemberAccount,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    member = member_generator.create_member_entity()
    company = company_generator.create_company_entity()

    transaction_generator.create_transaction(
        sending_account=member.account,
        receiving_account=company.product_account,
        amount_sent=Decimal(0),
        amount_received=Decimal(0),
    )

    response = use_case(member.id)
    assert response.transactions[0].transaction_volume == Decimal("0")
    assert str(response.transactions[0].transaction_volume) == "0"


@injection_test
def test_that_correct_info_is_generated_after_member_receives_wages(
    use_case: GetMemberAccount,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    member = member_generator.create_member_entity()
    company = company_generator.create_company_entity()

    transaction_generator.create_transaction(
        sending_account=company.work_account,
        receiving_account=member.account,
        amount_sent=Decimal(10),
        amount_received=Decimal(8.5),
    )

    response = use_case(member.id)
    assert len(response.transactions) == 1
    assert response.transactions[0].peer_name == company.name
    assert response.transactions[0].transaction_volume == Decimal(8.5)
    assert response.transactions[0].type == TransactionTypes.incoming_wages
    assert response.balance == Decimal(8.5)


@injection_test
def test_that_correct_info_for_company_is_generated_in_correct_order_after_several_transactions_of_different_kind(
    use_case: GetMemberAccount,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
    member_generator: MemberGenerator,
    datetime_service: FakeDatetimeService,
):
    company1 = company_generator.create_company_entity()
    company2 = company_generator.create_company_entity()
    member = member_generator.create_member_entity()

    # wages from comp1
    transaction_generator.create_transaction(
        sending_account=company1.work_account,
        receiving_account=member.account,
        amount_received=Decimal(12),
        date=datetime_service.now() + timedelta(hours=1),
    )
    # pay product of comp1
    transaction_generator.create_transaction(
        sending_account=member.account,
        receiving_account=company1.product_account,
        amount_sent=Decimal(5),
        date=datetime_service.now() + timedelta(hours=2),
    )
    # wages from comp2
    transaction_generator.create_transaction(
        sending_account=company2.work_account,
        receiving_account=member.account,
        amount_received=Decimal(2),
        date=datetime_service.now() + timedelta(hours=3),
    )

    response = use_case(member.id)
    assert len(response.transactions) == 3

    trans1 = response.transactions.pop()
    assert trans1.peer_name == company1.name
    assert trans1.transaction_volume == Decimal(12)

    trans2 = response.transactions.pop()
    assert trans2.peer_name == company1.name
    assert trans2.transaction_volume == Decimal(-5)

    trans3 = response.transactions.pop()
    assert trans3.peer_name == company2.name
    assert trans3.transaction_volume == Decimal(2)
