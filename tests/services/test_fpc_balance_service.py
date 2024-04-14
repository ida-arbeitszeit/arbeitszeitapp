from decimal import Decimal

from parameterized import parameterized

from arbeitszeit.fpc_balance import PublicFundService
from tests.data_generators import TransactionGenerator
from tests.use_cases.base_test_case import BaseTestCase


class PublicFundServiceCalculationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.service = self.injector.get(PublicFundService)
        self.transaction_generator = self.injector.get(TransactionGenerator)

    def test_fpc_balance_is_zero_if_no_public_plans_and_no_transactions(self) -> None:
        fpc_balance = self.service.calculate_fpc_balance()
        self.assertEqual(fpc_balance, 0)

    @parameterized.expand(
        [
            (Decimal(0.5), Decimal(5)),
            (Decimal(0), Decimal(10)),
            (Decimal(-0.5), Decimal(15)),
            (Decimal(1), Decimal(0)),
            (Decimal(1.5), Decimal(-5)),
        ]
    )
    def test_fpc_balance_if_no_public_plans_exist(
        self, amount_received: Decimal, expected_fpc_balance: Decimal
    ) -> None:
        test_company_id = self.company_generator.create_company()
        test_companies = self.service.database_gateway.get_companies().with_id(
            test_company_id
        )
        assert len(test_companies) == 1
        test_company = test_companies.first()
        assert test_company and test_company.id == test_company_id
        [
            self.transaction_generator.create_transaction(
                sending_account=test_company.work_account,
                amount_received=amount_received,
                amount_sent=Decimal(1),
            )
            for num in range(10)
        ]
        fpc_balance = self.service.calculate_fpc_balance()
        assert fpc_balance == expected_fpc_balance
