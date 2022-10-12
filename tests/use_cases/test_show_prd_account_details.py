from datetime import datetime, timedelta
from decimal import Decimal

from arbeitszeit.entities import SocialAccounting
from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases import ShowPRDAccountDetailsUseCase
from tests.data_generators import (
    CompanyGenerator,
    FakeDatetimeService,
    MemberGenerator,
    TransactionGenerator,
)

from .base_test_case import BaseTestCase


class UseCaseTester(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.show_prd_account_details = self.injector.get(ShowPRDAccountDetailsUseCase)
        self.transaction_generator = self.injector.get(TransactionGenerator)
        self.social_accounting = self.injector.get(SocialAccounting)

    def test_no_transactions_returned_when_no_transactions_took_place(self) -> None:
        self.member_generator.create_member()
        company = self.company_generator.create_company()

        response = self.show_prd_account_details(company.id)
        assert not response.transactions

    def test_balance_is_zero_when_no_transactions_took_place(self) -> None:
        self.member_generator.create_member()
        company = self.company_generator.create_company()

        response = self.show_prd_account_details(company.id)
        assert response.account_balance == 0

    def test_company_id_is_returned(self) -> None:
        self.member_generator.create_member()
        company = self.company_generator.create_company()

        response = self.show_prd_account_details(company.id)
        assert response.company_id == company.id

    def test_that_no_info_is_generated_after_company_buying_p(self) -> None:
        company1 = self.company_generator.create_company()
        company2 = self.company_generator.create_company()

        self.transaction_generator.create_transaction(
            sending_account=company1.means_account,
            receiving_account=company2.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(8.5),
        )

        response = self.show_prd_account_details(company1.id)
        assert len(response.transactions) == 0

    def test_that_no_info_is_generated_after_company_buying_r(self) -> None:
        company1 = self.company_generator.create_company()
        company2 = self.company_generator.create_company()

        self.transaction_generator.create_transaction(
            sending_account=company1.raw_material_account,
            receiving_account=company2.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(8.5),
        )

        response = self.show_prd_account_details(company1.id)
        assert len(response.transactions) == 0

    def test_that_no_info_is_generated_when_credit_for_r_is_granted(self) -> None:
        company = self.company_generator.create_company()

        self.transaction_generator.create_transaction(
            sending_account=self.social_accounting.account,
            receiving_account=company.raw_material_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(8.5),
        )
        response = self.show_prd_account_details(company.id)
        assert len(response.transactions) == 0

    def test_that_no_info_is_generated_when_credit_for_p_is_granted(self) -> None:
        company = self.company_generator.create_company()

        self.transaction_generator.create_transaction(
            sending_account=self.social_accounting.account,
            receiving_account=company.means_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(8.5),
        )
        response = self.show_prd_account_details(company.id)
        assert len(response.transactions) == 0

    def test_that_no_info_is_generated_when_credit_for_a_is_granted(self) -> None:
        company = self.company_generator.create_company()

        self.transaction_generator.create_transaction(
            sending_account=self.social_accounting.account,
            receiving_account=company.work_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(8.5),
        )
        response = self.show_prd_account_details(company.id)
        assert len(response.transactions) == 0

    def test_that_correct_info_is_generated_after_selling_of_consumer_product(
        self,
    ) -> None:
        member = self.member_generator.create_member()
        company = self.company_generator.create_company()

        self.transaction_generator.create_transaction(
            sending_account=member.account,
            receiving_account=company.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(8.5),
        )

        response = self.show_prd_account_details(company.id)
        assert len(response.transactions) == 1
        assert response.transactions[0].transaction_volume == Decimal(8.5)
        assert response.transactions[0].purpose is not None
        assert isinstance(response.transactions[0].date, datetime)
        assert (
            response.transactions[0].transaction_type
            == TransactionTypes.sale_of_consumer_product
        )
        assert response.account_balance == Decimal(8.5)

    def test_that_correct_info_is_generated_after_selling_of_means_of_production(
        self,
    ) -> None:
        company1 = self.company_generator.create_company()
        company2 = self.company_generator.create_company()

        self.transaction_generator.create_transaction(
            sending_account=company1.means_account,
            receiving_account=company2.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(8.5),
        )

        response = self.show_prd_account_details(company2.id)
        assert len(response.transactions) == 1
        assert response.transactions[0].transaction_volume == Decimal(8.5)
        assert response.transactions[0].purpose is not None
        assert isinstance(response.transactions[0].date, datetime)
        assert (
            response.transactions[0].transaction_type
            == TransactionTypes.sale_of_fixed_means
        )
        assert response.account_balance == Decimal(8.5)

    def test_that_correct_info_is_generated_after_selling_of_raw_material(self) -> None:
        company1 = self.company_generator.create_company()
        company2 = self.company_generator.create_company()

        self.transaction_generator.create_transaction(
            sending_account=company1.raw_material_account,
            receiving_account=company2.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(8.5),
        )

        response = self.show_prd_account_details(company2.id)
        assert len(response.transactions) == 1
        assert response.transactions[0].transaction_volume == Decimal(8.5)
        assert response.transactions[0].purpose is not None
        assert isinstance(response.transactions[0].date, datetime)
        assert (
            response.transactions[0].transaction_type
            == TransactionTypes.sale_of_liquid_means
        )
        assert response.account_balance == Decimal(8.5)

    def test_that_plotting_info_is_empty_when_no_transactions_occurred(self) -> None:
        self.member_generator.create_member()
        company = self.company_generator.create_company()

        response = self.show_prd_account_details(company.id)
        assert not response.plot.timestamps
        assert not response.plot.accumulated_volumes

    def test_that_plotting_info_is_generated_after_selling_of_consumer_product(
        self,
    ) -> None:
        member = self.member_generator.create_member()
        company = self.company_generator.create_company()

        self.transaction_generator.create_transaction(
            sending_account=member.account,
            receiving_account=company.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(8.5),
        )

        response = self.show_prd_account_details(company.id)
        assert response.plot.timestamps
        assert response.plot.accumulated_volumes

    def test_that_correct_plotting_info_is_generated_after_selling_of_two_consumer_products(
        self,
    ) -> None:
        member = self.member_generator.create_member()
        company = self.company_generator.create_company()
        datetime_service = FakeDatetimeService()

        trans1 = self.transaction_generator.create_transaction(
            sending_account=member.account,
            receiving_account=company.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(5),
            date=datetime_service.now() - timedelta(hours=2),
        )

        trans2 = self.transaction_generator.create_transaction(
            sending_account=member.account,
            receiving_account=company.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(10),
            date=datetime_service.now() - timedelta(hours=1),
        )

        response = self.show_prd_account_details(company.id)
        assert len(response.plot.timestamps) == 2
        assert len(response.plot.accumulated_volumes) == 2

        assert trans1.date in response.plot.timestamps
        assert trans2.date in response.plot.timestamps

        assert trans1.amount_received in response.plot.accumulated_volumes
        assert (
            trans1.amount_received + trans2.amount_received
        ) in response.plot.accumulated_volumes

    def test_that_plotting_info_is_generated_in_the_correct_order_after_selling_of_three_consumer_products(
        self,
    ) -> None:
        member = self.member_generator.create_member()
        company = self.company_generator.create_company()
        datetime_service = FakeDatetimeService()

        trans1 = self.transaction_generator.create_transaction(
            sending_account=member.account,
            receiving_account=company.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(1),
            date=datetime_service.now() - timedelta(hours=3),
        )

        trans2 = self.transaction_generator.create_transaction(
            sending_account=member.account,
            receiving_account=company.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(2),
            date=datetime_service.now() - timedelta(hours=2),
        )

        trans3 = self.transaction_generator.create_transaction(
            sending_account=member.account,
            receiving_account=company.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(3),
            date=datetime_service.now() - timedelta(hours=1),
        )

        response = self.show_prd_account_details(company.id)
        assert response.plot.timestamps[0] == trans1.date
        assert response.plot.timestamps[2] == trans3.date

        assert response.plot.accumulated_volumes[0] == trans1.amount_received
        assert response.plot.accumulated_volumes[2] == (
            trans1.amount_received + trans2.amount_received + trans3.amount_received
        )

    def test_that_no_buyer_is_shown_in_transaction_detail_when_transaction_is_debit_for_expected_sales(
        self,
    ) -> None:
        company = self.company_generator.create_company()

        self.transaction_generator.create_transaction(
            sending_account=self.social_accounting.account,
            receiving_account=company.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(5),
        )

        response = self.show_prd_account_details(company.id)
        assert response.transactions[0].buyer is None

    def test_that_correct_buyer_info_is_shown_when_company_sold_to_member(self) -> None:
        company = self.company_generator.create_company()
        member = self.member_generator.create_member()

        self.transaction_generator.create_transaction(
            sending_account=member.account,
            receiving_account=company.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(5),
        )

        response = self.show_prd_account_details(company.id)
        assert response.transactions[0].buyer
        assert response.transactions[0].buyer.buyer_is_member == True
        assert response.transactions[0].buyer.buyer_id == member.id
        assert response.transactions[0].buyer.buyer_name == member.name

    def test_that_correct_buyer_info_is_shown_when_company_sold_to_company(
        self,
    ) -> None:
        company1 = self.company_generator.create_company()
        company2 = self.company_generator.create_company()

        self.transaction_generator.create_transaction(
            sending_account=company1.means_account,
            receiving_account=company2.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(5),
        )

        response = self.show_prd_account_details(company2.id)
        assert response.transactions[0].buyer
        assert response.transactions[0].buyer.buyer_is_member == False
        assert response.transactions[0].buyer.buyer_id == company1.id
        assert response.transactions[0].buyer.buyer_name == company1.name
