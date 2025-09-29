from decimal import Decimal
from uuid import UUID

from parameterized import parameterized

from arbeitszeit import records
from arbeitszeit.interactors.get_member_account import GetMemberAccountInteractor
from arbeitszeit.transfers import TransferType
from tests.interactors.base_test_case import BaseTestCase


class GetMemberAccountTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.interactor = self.injector.get(GetMemberAccountInteractor)
        self.social_accounting_name = self.injector.get(
            records.SocialAccounting
        ).get_name()

    def test_that_balance_is_zero_when_no_transfer_took_place(
        self,
    ) -> None:
        member = self.member_generator.create_member()
        response = self.interactor.execute(member)
        assert response.balance == 0

    def test_that_transfers_is_empty_when_no_transfer_took_place(self) -> None:
        member = self.member_generator.create_member()
        response = self.interactor.execute(member)
        assert not response.transfers

    def test_that_transfers_is_empty_when_member_is_not_involved_in_transfer(
        self,
    ) -> None:
        member_of_interest = self.member_generator.create_member()
        self.consumption_generator.create_private_consumption()
        response = self.interactor.execute(member_of_interest)
        assert not response.transfers

    def test_that_correct_info_is_generated_after_member_consumes_product(self) -> None:
        expected_company_name = "test company 123"
        member = self.member_generator.create_member()
        company = self.company_generator.create_company(name=expected_company_name)
        plan = self.plan_generator.create_plan(
            planner=company,
            costs=records.ProductionCosts(
                labour_cost=Decimal(10),
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
            ),
            amount=1,
        )
        self.consumption_generator.create_private_consumption(
            consumer=member, amount=1, plan=plan
        )
        response = self.interactor.execute(member)
        assert len(response.transfers) == 1
        assert response.transfers[0].transfer_party.name == expected_company_name
        assert response.transfers[0].volume == Decimal(-10)
        assert response.transfers[0].type == TransferType.private_consumption
        assert response.balance == Decimal(-10)

    def test_that_a_transfer_with_volume_zero_is_shown_correctly(self) -> None:
        expected_company_name = "test company 123"
        member = self.member_generator.create_member()
        company = self.company_generator.create_company(name=expected_company_name)
        plan = self.plan_generator.create_plan(
            planner=company,
            costs=records.ProductionCosts(
                labour_cost=Decimal(0),
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
            ),
            amount=1,
        )
        self.consumption_generator.create_private_consumption(
            consumer=member, amount=1, plan=plan
        )
        response = self.interactor.execute(member)
        assert response.transfers[0].volume == Decimal("0")
        assert str(response.transfers[0].volume) == "0"

    def test_that_after_member_has_worked_info_on_certificates_and_taxes_are_generated(
        self,
    ) -> None:
        member = self.member_generator.create_member()
        company = self.company_generator.create_company(
            workers=[member],
        )
        self.registered_hours_worked_generator.register_hours_worked(
            company=company,
            worker=member,
            hours=Decimal("8.5"),
        )
        response = self.interactor.execute(member)
        assert len(response.transfers) == 2
        assert response.transfers[0].type == TransferType.taxes
        assert response.transfers[1].type == TransferType.work_certificates

    def test_that_balance_is_correct_after_member_has_worked(self) -> None:
        member = self.member_generator.create_member()
        company = self.company_generator.create_company(
            workers=[member],
        )
        self.registered_hours_worked_generator.register_hours_worked(
            company=company,
            worker=member,
            hours=Decimal("8.5"),
        )
        response = self.interactor.execute(member)
        assert response.balance == Decimal("8.5")

    def test_that_correct_tax_info_is_generated(self) -> None:
        expected_company_name = "test company name"
        member = self.member_generator.create_member()
        company = self.company_generator.create_company(
            workers=[member], name=expected_company_name
        )
        self.registered_hours_worked_generator.register_hours_worked(
            company=company,
            worker=member,
            hours=Decimal("8.5"),
        )
        response = self.interactor.execute(member)
        transfer = response.transfers[0]
        assert transfer.transfer_party.name == self.social_accounting_name
        assert transfer.type == TransferType.taxes
        assert transfer.volume == Decimal("0")

    def test_that_correct_work_certificates_info_is_generated(self) -> None:
        expected_company_name = "test company name"
        member = self.member_generator.create_member()
        company = self.company_generator.create_company(
            workers=[member], name=expected_company_name
        )
        self.registered_hours_worked_generator.register_hours_worked(
            company=company,
            worker=member,
            hours=Decimal("8.5"),
        )
        response = self.interactor.execute(member)
        transfer = response.transfers[1]
        assert transfer.transfer_party.name == expected_company_name
        assert transfer.volume == Decimal(8.5)
        assert transfer.type == TransferType.work_certificates

    def test_that_correct_peer_name_info_is_generated_in_correct_order_after_several_transfers_of_different_kind(
        self,
    ) -> None:
        company1_name = "test company 1"
        company2_name = "test company 2"
        member = self.member_generator.create_member()
        company1 = self.company_generator.create_company(
            workers=[member], name=company1_name
        )
        company1_plan = self.plan_generator.create_plan(
            planner=company1,
            costs=records.ProductionCosts(
                labour_cost=Decimal(5), means_cost=Decimal(0), resource_cost=Decimal(0)
            ),
            amount=1,
        )
        company2 = self.company_generator.create_company(
            workers=[member], name=company2_name
        )
        # register hours
        self.registered_hours_worked_generator.register_hours_worked(
            company=company1,
            worker=member,
            hours=Decimal("12"),
        )
        # consume
        self.consumption_generator.create_private_consumption(
            consumer=member,
            plan=company1_plan,
            amount=1,
        )
        # register hours
        self.registered_hours_worked_generator.register_hours_worked(
            company=company2,
            worker=member,
            hours=Decimal("2"),
        )
        response = self.interactor.execute(member)
        assert len(response.transfers) == 5  # 1 consumption, 2 work certificates, 2 tax

        trans1 = response.transfers.pop()
        assert trans1.transfer_party.name == company1_name

        trans2 = response.transfers.pop()
        assert trans2.transfer_party.name == self.social_accounting_name

        trans3 = response.transfers.pop()
        assert trans3.transfer_party.name == company1_name

        trans4 = response.transfers.pop()
        assert trans4.transfer_party.name == company2_name

        trans5 = response.transfers.pop()
        assert trans5.transfer_party.name == self.social_accounting_name

    @parameterized.expand([(True,), (False,)])
    def test_that_transfer_is_set_as_debit_transfer_if_that_is_the_case(
        self, is_debit_transfer: bool
    ) -> None:
        member = self.member_generator.create_member()
        account = self.get_account_of_member(member)
        if is_debit_transfer:
            self.transfer_generator.create_transfer(debit_account=account)
        else:
            self.transfer_generator.create_transfer(credit_account=account)
        response = self.interactor.execute(member)
        assert len(response.transfers) == 1
        assert response.transfers[0].is_debit_transfer == is_debit_transfer

    def get_account_of_member(self, member: UUID) -> UUID:
        account = self.database_gateway.get_accounts().owned_by_member(member).first()
        assert account
        return account.id
