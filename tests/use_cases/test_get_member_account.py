from decimal import Decimal

from arbeitszeit import records
from arbeitszeit.transfers import TransferType
from arbeitszeit.use_cases.get_member_account import GetMemberAccount
from arbeitszeit.use_cases.register_hours_worked import (
    RegisterHoursWorked,
    RegisterHoursWorkedRequest,
)
from tests.data_generators import (
    CompanyGenerator,
    ConsumptionGenerator,
    MemberGenerator,
    PlanGenerator,
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
    consumption_generator: ConsumptionGenerator,
):
    member_of_interest = member_generator.create_member()
    consumption_generator.create_private_consumption()
    response = use_case(member_of_interest)
    assert not response.transactions


@injection_test
def test_that_correct_info_is_generated_after_member_consumes_product(
    use_case: GetMemberAccount,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    consumption_generator: ConsumptionGenerator,
    plan_generator: PlanGenerator,
):
    expected_company_name = "test company 123"
    member = member_generator.create_member()
    company = company_generator.create_company(name=expected_company_name)
    plan = plan_generator.create_plan(
        planner=company,
        costs=records.ProductionCosts(
            labour_cost=Decimal(10),
            means_cost=Decimal(0),
            resource_cost=Decimal(0),
        ),
        amount=1,
    )
    consumption_generator.create_private_consumption(
        consumer=member, amount=1, plan=plan
    )
    response = use_case(member)
    assert len(response.transactions) == 1
    assert response.transactions[0].peer_name == expected_company_name
    assert response.transactions[0].transaction_volume == Decimal(-10)
    assert response.transactions[0].type == TransferType.private_consumption
    assert response.balance == Decimal(-10)


@injection_test
def test_that_a_transaction_with_volume_zero_is_shown_correctly(
    use_case: GetMemberAccount,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    consumption_generator: ConsumptionGenerator,
    plan_generator: PlanGenerator,
):
    expected_company_name = "test company 123"
    member = member_generator.create_member()
    company = company_generator.create_company(name=expected_company_name)
    plan = plan_generator.create_plan(
        planner=company,
        costs=records.ProductionCosts(
            labour_cost=Decimal(0),
            means_cost=Decimal(0),
            resource_cost=Decimal(0),
        ),
        amount=1,
    )
    consumption_generator.create_private_consumption(
        consumer=member, amount=1, plan=plan
    )
    response = use_case(member)
    assert response.transactions[0].transaction_volume == Decimal("0")
    assert str(response.transactions[0].transaction_volume) == "0"


@injection_test
def test_that_after_member_has_worked_info_on_certificates_and_taxes_are_generated(
    use_case: GetMemberAccount,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    register_hours_worked: RegisterHoursWorked,
):
    member = member_generator.create_member()
    company = company_generator.create_company(
        workers=[member],
    )
    register_hours_worked(
        use_case_request=RegisterHoursWorkedRequest(
            company_id=company,
            worker_id=member,
            hours_worked=Decimal("8.5"),
        )
    )

    response = use_case(member)
    assert len(response.transactions) == 2
    assert response.transactions[0].type == TransferType.taxes
    assert response.transactions[1].type == TransferType.work_certificates


@injection_test
def test_that_balance_is_correct_after_member_has_worked(
    use_case: GetMemberAccount,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    register_hours_worked: RegisterHoursWorked,
):
    member = member_generator.create_member()
    company = company_generator.create_company(
        workers=[member],
    )
    register_hours_worked(
        use_case_request=RegisterHoursWorkedRequest(
            company_id=company,
            worker_id=member,
            hours_worked=Decimal("8.5"),
        )
    )
    response = use_case(member)
    assert response.balance == Decimal("8.5")


@injection_test
def test_that_correct_tax_info_is_generated(
    use_case: GetMemberAccount,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    register_hours_worked: RegisterHoursWorked,
    social_accounting: records.SocialAccounting,
):
    expected_company_name = "test company name"
    member = member_generator.create_member()
    company = company_generator.create_company(
        workers=[member], name=expected_company_name
    )
    register_hours_worked(
        use_case_request=RegisterHoursWorkedRequest(
            company_id=company,
            worker_id=member,
            hours_worked=Decimal("8.5"),
        )
    )
    response = use_case(member)
    transfer = response.transactions[0]
    assert transfer.peer_name == social_accounting.get_name()
    assert transfer.type == TransferType.taxes
    assert transfer.transaction_volume == Decimal("0")


@injection_test
def test_that_correct_work_certificates_info_is_generated(
    use_case: GetMemberAccount,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    register_hours_worked: RegisterHoursWorked,
):
    expected_company_name = "test company name"
    member = member_generator.create_member()
    company = company_generator.create_company(
        workers=[member], name=expected_company_name
    )
    register_hours_worked(
        use_case_request=RegisterHoursWorkedRequest(
            company_id=company,
            worker_id=member,
            hours_worked=Decimal("8.5"),
        )
    )
    response = use_case(member)
    transfer = response.transactions[1]
    assert transfer.peer_name == expected_company_name
    assert transfer.transaction_volume == Decimal(8.5)
    assert transfer.type == TransferType.work_certificates


@injection_test
def test_that_correct_peer_name_info_is_generated_in_correct_order_after_several_transactions_of_different_kind(
    use_case: GetMemberAccount,
    company_generator: CompanyGenerator,
    member_generator: MemberGenerator,
    register_hours_worked: RegisterHoursWorked,
    consumption_generator: ConsumptionGenerator,
    plan_generator: PlanGenerator,
    social_accounting: records.SocialAccounting,
):
    company1_name = "test company 1"
    company2_name = "test company 2"
    member = member_generator.create_member()
    company1 = company_generator.create_company(workers=[member], name=company1_name)
    company1_plan = plan_generator.create_plan(
        planner=company1,
        costs=records.ProductionCosts(
            labour_cost=Decimal(5), means_cost=Decimal(0), resource_cost=Decimal(0)
        ),
        amount=1,
    )
    company2 = company_generator.create_company(workers=[member], name=company2_name)
    # register hours
    register_hours_worked(
        use_case_request=RegisterHoursWorkedRequest(
            company_id=company1,
            worker_id=member,
            hours_worked=Decimal("12"),
        )
    )
    # consume
    consumption_generator.create_private_consumption(
        consumer=member,
        plan=company1_plan,
        amount=1,
    )
    # register hours
    register_hours_worked(
        use_case_request=RegisterHoursWorkedRequest(
            company_id=company2,
            worker_id=member,
            hours_worked=Decimal("2"),
        )
    )
    response = use_case(member)
    assert len(response.transactions) == 5  # 1 consumption, 2 work certificates, 2 tax

    trans1 = response.transactions.pop()
    assert trans1.peer_name == company1_name

    trans2 = response.transactions.pop()
    assert trans2.peer_name == social_accounting.get_name()

    trans3 = response.transactions.pop()
    assert trans3.peer_name == company1_name

    trans4 = response.transactions.pop()
    assert trans4.peer_name == company2_name

    trans5 = response.transactions.pop()
    assert trans5.peer_name == social_accounting.get_name()
