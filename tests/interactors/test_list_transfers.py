from decimal import Decimal
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from parameterized import parameterized

from arbeitszeit.interactors.list_transfers import (
    AccountOwnerType,
    ListTransfersInteractor,
    Request,
    Response,
)
from arbeitszeit.records import ProductionCosts, SocialAccounting
from arbeitszeit.transfers import TransferType
from tests.datetime_service import datetime_utc
from tests.interactors.base_test_case import BaseTestCase


class _AccountOwnerType(Enum):
    member = auto()
    company = auto()
    social_accounting = auto()
    cooperation = auto()


class TransferTestBase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(ListTransfersInteractor)

    def list_transfers(self) -> Response:
        return self.interactor.list_transfers(self.create_request())

    def create_request(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> Request:
        return Request(limit=limit, offset=offset)

    def create_transfer_from(
        self,
        account_owner_type: _AccountOwnerType,
        name: str = "Some Account Owner",
    ) -> None:
        if account_owner_type == _AccountOwnerType.member:
            self.transfer_generator.create_transfer(
                debit_account=self._get_member_account(member_name=name)
            )
        elif account_owner_type == _AccountOwnerType.company:
            self.transfer_generator.create_transfer(
                debit_account=self._get_company_account(company_name=name)
            )
        elif account_owner_type == _AccountOwnerType.social_accounting:
            self.transfer_generator.create_transfer(
                debit_account=self._get_social_accounting_account()
            )
        elif account_owner_type == _AccountOwnerType.cooperation:
            self.transfer_generator.create_transfer(
                debit_account=self._get_cooperation_account(cooperation_name=name)
            )

    def create_transfer_to(
        self, account_owner_type: _AccountOwnerType, name: str = "Some Account Owner"
    ) -> None:
        if account_owner_type == _AccountOwnerType.member:
            self.transfer_generator.create_transfer(
                credit_account=self._get_member_account(member_name=name)
            )
        elif account_owner_type == _AccountOwnerType.company:
            self.transfer_generator.create_transfer(
                credit_account=self._get_company_account(company_name=name)
            )
        elif account_owner_type == _AccountOwnerType.social_accounting:
            self.transfer_generator.create_transfer(
                credit_account=self._get_social_accounting_account()
            )
        elif account_owner_type == _AccountOwnerType.cooperation:
            self.transfer_generator.create_transfer(
                credit_account=self._get_cooperation_account(cooperation_name=name)
            )

    def _get_member_account(self, member_name: str) -> UUID:
        member = self.member_generator.create_member(name=member_name)
        account = self.database_gateway.get_accounts().owned_by_member(member).first()
        assert account
        return account.id

    def _get_company_account(self, company_name: str) -> UUID:
        company = self.company_generator.create_company(name=company_name)
        account = self.database_gateway.get_accounts().owned_by_company(company).first()
        assert account
        return account.id

    def _get_social_accounting_account(self) -> UUID:
        social_accounting = self.injector.get(SocialAccounting)
        account = social_accounting.account_psf
        return account

    def _get_cooperation_account(self, cooperation_name: str) -> UUID:
        cooperation_id = self.cooperation_generator.create_cooperation(
            name=cooperation_name
        )
        cooperation = (
            self.database_gateway.get_cooperations().with_id(cooperation_id).first()
        )
        assert cooperation
        return cooperation.account


class ListTransfersTests(TransferTestBase):
    def test_that_empty_list_is_returned_if_no_transfers_exist(self) -> None:
        response = self.list_transfers()
        assert not response.transfers


class LimitAndOffsetTests(TransferTestBase):
    @parameterized.expand(
        [
            (None, None, 3),
            (3, None, 3),
            (3, 0, 3),
            (1, 0, 1),
            (2, 0, 2),
            (3, 2, 1),
            (3, 1, 2),
        ]
    )
    def test_that_limit_and_offset_are_applied_correctly_when_there_are_three_transfers_in_the_system(
        self, limit: int, offset: int, expected_results: int
    ) -> None:
        self.plan_generator.create_plan()
        request = self.create_request(limit=limit, offset=offset)
        response = self.interactor.list_transfers(request)
        assert response.total_results == 3
        assert len(response.transfers) == expected_results


class ListTransfersOfApprovedProductivePlanTests(TransferTestBase):
    def test_that_three_transfers_are_returned_after_approval_of_plan(self) -> None:
        self.plan_generator.create_plan()
        response = self.list_transfers()
        assert len(response.transfers) == 3
        assert response.total_results == 3

    def test_that_six_transfers_are_returned_after_approval_of_two_plans(self) -> None:
        self.plan_generator.create_plan()
        self.plan_generator.create_plan()
        response = self.list_transfers()
        assert len(response.transfers) == 6
        assert response.total_results == 6

    def test_that_all_transfers_have_correct_date(self) -> None:
        expected_date = datetime_utc(2024, 1, 1, 12, 0)
        self.datetime_service.freeze_time(expected_date)
        self.plan_generator.create_plan()
        response = self.list_transfers()
        assert all(transfer.date == expected_date for transfer in response.transfers)

    def test_that_debit_account_is_planners_prd_account_for_all_transfers(self) -> None:
        planner = self.company_generator.create_company_record()
        self.plan_generator.create_plan(planner=planner.id)
        response = self.list_transfers()
        assert all(
            transfer.debit_account == planner.product_account
            for transfer in response.transfers
        )

    def test_that_planning_company_is_shown_as_debtor_and_creditor_for_all_transfers(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(planner=planner)
        response = self.list_transfers()
        assert all(transfer.debtor == planner for transfer in response.transfers)
        assert all(transfer.creditor == planner for transfer in response.transfers)

    def test_that_one_of_three_transfers_is_credited_to_planners_means_account(
        self,
    ) -> None:
        planner = self.company_generator.create_company_record()
        self.plan_generator.create_plan(planner=planner.id)
        response = self.list_transfers()
        assert len(response.transfers) == 3
        assert any(
            transfer.credit_account == planner.means_account
            for transfer in response.transfers
        )

    @parameterized.expand(
        [
            (Decimal("100.00"),),
            (Decimal("200.00"),),
        ]
    )
    def test_that_transfer_to_means_account_has_correct_value_and_type(
        self, planned_means: Decimal
    ) -> None:
        self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=Decimal(0),
                resource_cost=Decimal(0),
                means_cost=planned_means,
            )
        )
        response = self.list_transfers()
        assert any(
            transfer.value == planned_means
            and transfer.transfer_type == TransferType.credit_p
            for transfer in response.transfers
        )

    @parameterized.expand(
        [
            (Decimal("100.00"),),
            (Decimal("200.00"),),
        ]
    )
    def test_that_transfer_to_raw_materials_account_has_correct_value_and_type(
        self, planned_raw_materials: Decimal
    ) -> None:
        self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=Decimal(0),
                resource_cost=planned_raw_materials,
                means_cost=Decimal(0),
            )
        )
        response = self.list_transfers()
        assert any(
            transfer.value == planned_raw_materials
            and transfer.transfer_type == TransferType.credit_r
            for transfer in response.transfers
        )

    @parameterized.expand(
        [
            (Decimal("100.00"),),
            (Decimal("200.00"),),
        ]
    )
    def test_that_transfer_to_work_account_has_correct_value_and_type(
        self, planned_labour: Decimal
    ) -> None:
        self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=planned_labour,
                resource_cost=Decimal(0),
                means_cost=Decimal(0),
            )
        )
        response = self.list_transfers()
        assert any(
            transfer.value == planned_labour
            and transfer.transfer_type == TransferType.credit_a
            for transfer in response.transfers
        )

    def test_that_one_of_three_transfers_is_credited_to_planners_raw_material_account(
        self,
    ) -> None:
        planner = self.company_generator.create_company_record()
        self.plan_generator.create_plan(planner=planner.id)
        response = self.list_transfers()
        assert len(response.transfers) == 3
        assert any(
            transfer.credit_account == planner.raw_material_account
            for transfer in response.transfers
        )

    def test_that_one_of_three_transfers_is_credited_to_planners_work_account(
        self,
    ) -> None:
        planner = self.company_generator.create_company_record()
        self.plan_generator.create_plan(planner=planner.id)
        response = self.list_transfers()
        assert len(response.transfers) == 3
        assert any(
            transfer.credit_account == planner.work_account
            for transfer in response.transfers
        )

    def test_that_newest_transfer_is_returned_first(self) -> None:
        date1 = datetime_utc(2024, 1, 1, 12, 0)
        self.datetime_service.freeze_time(date1)
        self.plan_generator.create_plan()

        date2 = datetime_utc(2024, 1, 2, 12, 0)
        self.datetime_service.freeze_time(date2)
        self.plan_generator.create_plan()

        response = self.list_transfers()

        assert len(response.transfers) == 6
        assert response.transfers[0].date == date2


class AccountIdTests(TransferTestBase):
    def test_that_debit_account_is_none_if_debtor_is_a_member(self) -> None:
        self.create_transfer_from(_AccountOwnerType.member)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].debit_account is None

    def test_that_credit_account_is_none_if_creditor_is_a_member(self) -> None:
        self.create_transfer_to(_AccountOwnerType.member)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].credit_account is None

    def test_that_debit_account_is_not_none_if_debtor_is_a_company(self) -> None:
        self.create_transfer_from(_AccountOwnerType.company)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].debit_account is not None

    def test_that_credit_account_is_not_none_if_creditor_is_a_company(self) -> None:
        self.create_transfer_to(_AccountOwnerType.company)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].credit_account is not None

    def test_that_debit_account_is_not_none_if_debtor_is_social_accounting(
        self,
    ) -> None:
        self.create_transfer_from(_AccountOwnerType.social_accounting)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].debit_account is not None

    def test_that_credit_account_is_not_none_if_creditor_is_social_accounting(
        self,
    ) -> None:
        self.create_transfer_to(_AccountOwnerType.social_accounting)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].credit_account is not None

    def test_that_debit_account_is_not_none_if_debtor_is_cooperation(self) -> None:
        self.create_transfer_from(_AccountOwnerType.cooperation)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].debit_account is not None

    def test_that_credit_account_is_not_none_if_creditor_is_cooperation(self) -> None:
        self.create_transfer_to(_AccountOwnerType.cooperation)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].credit_account is not None


class AccountOwnerIdTests(TransferTestBase):
    def test_that_debtor_id_is_none_if_debtor_is_a_member(self) -> None:
        self.create_transfer_from(_AccountOwnerType.member)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].debtor is None

    def test_that_creditor_id_is_none_if_creditor_is_a_member(self) -> None:
        self.create_transfer_to(_AccountOwnerType.member)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].creditor is None

    def test_that_debtor_id_is_not_none_if_debtor_is_a_company(self) -> None:
        self.create_transfer_from(_AccountOwnerType.company)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].debtor is not None

    def test_that_creditor_id_is_not_none_if_creditor_is_a_company(self) -> None:
        self.create_transfer_to(_AccountOwnerType.company)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].creditor is not None

    def test_that_debtor_id_is_not_none_if_debtor_is_social_accounting(self) -> None:
        self.create_transfer_from(_AccountOwnerType.social_accounting)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].debtor is not None

    def test_that_creditor_id_is_not_none_if_creditor_is_social_accounting(
        self,
    ) -> None:
        self.create_transfer_to(_AccountOwnerType.social_accounting)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].creditor is not None

    def test_that_debtor_id_is_not_none_if_debtor_is_cooperation(self) -> None:
        self.create_transfer_from(_AccountOwnerType.cooperation)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].debtor is not None

    def test_that_creditor_id_is_not_none_if_creditor_is_cooperation(self) -> None:
        self.create_transfer_to(_AccountOwnerType.cooperation)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].creditor is not None


class AccountOwnerNameTests(TransferTestBase):
    def test_that_debtor_name_is_none_if_debtor_is_a_member(self) -> None:
        self.create_transfer_from(_AccountOwnerType.member)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].debtor_name is None

    def test_that_creditor_name_is_none_if_creditor_is_a_member(self) -> None:
        self.create_transfer_to(_AccountOwnerType.member)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].creditor_name is None

    def test_that_debtor_name_is_none_if_debtor_is_social_accounting(self) -> None:
        self.create_transfer_from(_AccountOwnerType.social_accounting)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].debtor_name is None

    def test_that_creditor_name_is_none_if_creditor_is_social_accounting(self) -> None:
        self.create_transfer_to(_AccountOwnerType.social_accounting)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].creditor_name is None

    def test_that_debtor_name_is_correct_name_of_company(self) -> None:
        expected_name = "Some test company name"
        self.create_transfer_from(_AccountOwnerType.company, name=expected_name)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].debtor_name == expected_name

    def test_that_creditor_name_is_correct_name_of_company(self) -> None:
        expected_name = "Some test company name"
        self.create_transfer_to(_AccountOwnerType.company, name=expected_name)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].creditor_name == expected_name

    def test_that_debtor_name_is_correct_name_of_cooperation(self) -> None:
        expected_name = "Some test cooperation name"
        self.create_transfer_from(_AccountOwnerType.cooperation, name=expected_name)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].debtor_name == expected_name

    def test_that_creditor_name_is_correct_name_of_cooperation(self) -> None:
        expected_name = "Some test cooperation name"
        self.create_transfer_to(_AccountOwnerType.cooperation, name=expected_name)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].creditor_name == expected_name


class AccountOwnerTypeTests(TransferTestBase):
    def test_that_correct_account_owner_type_is_returned_if_debtor_is_member(
        self,
    ) -> None:
        self.create_transfer_from(_AccountOwnerType.member)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].debtor_type == AccountOwnerType.member

    def test_that_correct_account_owner_type_is_returned_if_debtor_is_company(
        self,
    ) -> None:
        self.create_transfer_from(_AccountOwnerType.company)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].debtor_type == AccountOwnerType.company

    def test_that_correct_account_owner_type_is_returned_if_debtor_is_cooperation(
        self,
    ) -> None:
        self.create_transfer_from(_AccountOwnerType.cooperation)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].debtor_type == AccountOwnerType.cooperation

    def test_that_correct_account_owner_type_is_returned_if_debtor_is_social_accounting(
        self,
    ) -> None:
        self.create_transfer_from(_AccountOwnerType.social_accounting)
        response = self.list_transfers()
        assert len(response.transfers) == 1
        assert response.transfers[0].debtor_type == AccountOwnerType.social_accounting
