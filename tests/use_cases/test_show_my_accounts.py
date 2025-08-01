from decimal import Decimal
from uuid import UUID

from parameterized import parameterized

from arbeitszeit.records import ProductionCosts
from arbeitszeit.use_cases.register_hours_worked import (
    RegisterHoursWorked,
    RegisterHoursWorkedRequest,
)
from arbeitszeit.use_cases.show_company_accounts import (
    ShowCompanyAccounts,
    ShowCompanyAccountsRequest,
)
from tests.company import CompanyManager
from tests.use_cases.base_test_case import BaseTestCase


class ShowCompanyAccountsTest(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(ShowCompanyAccounts)
        self.company_manager = self.injector.get(CompanyManager)

    def test_that_response_returns_the_company_id_that_was_requested(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        response = self.use_case(request=ShowCompanyAccountsRequest(company=company))
        assert response.company == company

    def test_that_list_of_balances_has_four_entries_when_no_transfers_took_place(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        response = self.use_case(request=ShowCompanyAccountsRequest(company=company))
        assert len(response.balances) == 4

    def test_that_all_balances_are_zero_when_no_transfers_took_place(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        response = self.use_case(request=ShowCompanyAccountsRequest(company=company))
        for balance in response.balances:
            assert balance == Decimal(0)

    @parameterized.expand(
        [
            (Decimal(0),),
            (Decimal(5.5),),
        ]
    )
    def test_that_balance_of_mean_account_reflects_consumption_of_fixed_means_that_took_place(
        self, consumed_cost: Decimal
    ) -> None:
        company = self.company_generator.create_company()
        self.consume_fixed_means(company, consumed_cost)
        response = self.use_case(request=ShowCompanyAccountsRequest(company=company))
        assert response.balances[0] == Decimal(-consumed_cost)

    @parameterized.expand(
        [
            (Decimal(0),),
            (Decimal(5.5),),
        ]
    )
    def test_that_balance_of_raw_material_account_reflects_consumption_of_liquid_means_that_took_place(
        self, consumed_cost: Decimal
    ) -> None:
        company = self.company_generator.create_company()
        self.consume_liquid_means(company, consumed_cost)
        response = self.use_case(request=ShowCompanyAccountsRequest(company=company))
        assert response.balances[1] == Decimal(-consumed_cost)

    @parameterized.expand(
        [
            (Decimal(1),),
            (Decimal(5.5),),
        ]
    )
    def test_that_balance_of_work_account_reflects_registered_work_that_took_place(
        self, hours_worked: Decimal
    ) -> None:
        company = self.company_generator.create_company()
        self.register_hours_worked(company, hours_worked)
        response = self.use_case(request=ShowCompanyAccountsRequest(company=company))
        assert response.balances[2] == Decimal(-hours_worked)

    @parameterized.expand(
        [
            (Decimal(0),),
            (Decimal(5.5),),
        ]
    )
    def test_that_balance_of_product_account_reflects_private_consumption_that_took_place(
        self, price: Decimal
    ) -> None:
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
                labour_cost=price,
            ),
            amount=1,
            planner=company,
        )
        balance_before_consumption = self.use_case(
            request=ShowCompanyAccountsRequest(company=company)
        ).balances[3]
        self.consumption_generator.create_private_consumption(
            consumer=self.member_generator.create_member(),
            plan=plan,
            amount=1,
        )
        balance_after_consumption = self.use_case(
            request=ShowCompanyAccountsRequest(company=company)
        ).balances[3]
        assert balance_after_consumption == balance_before_consumption + price

    def consume_fixed_means(self, consuming_company: UUID, costs: Decimal) -> None:
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                means_cost=costs,
                resource_cost=Decimal(0),
                labour_cost=Decimal(0),
            ),
            amount=1,
        )
        self.consumption_generator.create_fixed_means_consumption(
            consumer=consuming_company,
            plan=plan,
            amount=1,
        )

    def consume_liquid_means(self, consuming_company: UUID, costs: Decimal) -> None:
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                means_cost=costs,
                resource_cost=Decimal(0),
                labour_cost=Decimal(0),
            ),
            amount=1,
        )
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consuming_company,
            plan=plan,
            amount=1,
        )

    def register_hours_worked(self, registering_company: UUID, hours: Decimal) -> None:
        member = self.member_generator.create_member()
        self.company_manager.add_worker_to_company(registering_company, member)
        use_case = self.injector.get(RegisterHoursWorked)
        response = use_case(
            use_case_request=RegisterHoursWorkedRequest(
                company_id=registering_company,
                worker_id=member,
                hours_worked=hours,
            )
        )
        assert not response.is_rejected
