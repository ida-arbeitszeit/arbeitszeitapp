from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit.transfers.transfer_type import TransferType
from arbeitszeit.use_cases import list_transfers
from arbeitszeit_web.pagination import DEFAULT_PAGE_SIZE
from arbeitszeit_web.www.presenters.list_transfers_presenter import (
    ListTransfersPresenter,
)
from tests.datetime_service import datetime_utc
from tests.www.base_test_case import BaseTestCase


class ListTransfersPresenterBase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ListTransfersPresenter)

    def create_transfer_entry(
        self,
        date: datetime = datetime_utc(2024, 1, 1, 12, 0),
        debtor: UUID | None = UUID("00000000-0000-0000-0000-000000000000"),
        debit_account: UUID | None = UUID("00000000-0000-0000-0000-000000000000"),
        debtor_name: str | None = "Debtor",
        debtor_type: list_transfers.AccountOwnerType = list_transfers.AccountOwnerType.company,
        creditor: UUID | None = UUID("00000000-0000-0000-0000-000000000000"),
        credit_account: UUID | None = UUID("00000000-0000-0000-0000-000000000000"),
        creditor_name: str | None = "Creditor",
        creditor_type: list_transfers.AccountOwnerType = list_transfers.AccountOwnerType.company,
        value: Decimal = Decimal("10.00"),
        transfer_type: TransferType = TransferType.credit_p,
    ) -> list_transfers.TransferEntry:
        return list_transfers.TransferEntry(
            date=date,
            debtor=debtor,
            debit_account=debit_account,
            debtor_name=debtor_name,
            debtor_type=debtor_type,
            creditor=creditor,
            credit_account=credit_account,
            creditor_name=creditor_name,
            creditor_type=creditor_type,
            value=value,
            transfer_type=transfer_type,
        )

    def create_use_case_response(
        self,
        transfers: list[list_transfers.TransferEntry] | None = None,
        total_results: int = 10,
    ) -> list_transfers.Response:
        if transfers is None:
            transfers = []
        return list_transfers.Response(
            transfers=transfers,
            total_results=total_results,
        )


class PaginationTests(ListTransfersPresenterBase):
    @parameterized.expand(
        [
            (DEFAULT_PAGE_SIZE - 1, False),
            (DEFAULT_PAGE_SIZE, False),
            (DEFAULT_PAGE_SIZE + 1, True),
        ]
    )
    def test_pagination_is_visible_if_total_results_is_greater_than_default_page_size(
        self, total_results: int, is_visible: bool
    ) -> None:
        uc_response = self.create_use_case_response(total_results=total_results)
        view_model = self.presenter.present(uc_response)
        assert view_model.pagination.is_visible is is_visible

    @parameterized.expand(
        [
            (DEFAULT_PAGE_SIZE - 1, 1),
            (DEFAULT_PAGE_SIZE, 1),
            (DEFAULT_PAGE_SIZE + 1, 2),
        ]
    )
    def test_number_of_pages_is_correct_based_on_total_results_and_page_size(
        self, total_results: int, num_of_pages: int
    ) -> None:
        uc_response = self.create_use_case_response(total_results=total_results)
        view_model = self.presenter.present(uc_response)
        assert len(view_model.pagination.pages) == num_of_pages


class ShosResultsTests(ListTransfersPresenterBase):
    def test_show_results_is_false_if_no_transfers(self) -> None:
        uc_response = self.create_use_case_response(transfers=[])
        view_model = self.presenter.present(uc_response)
        assert not view_model.show_results

    def test_show_results_is_true_if_transfers_exist(self) -> None:
        uc_response = self.create_use_case_response(
            transfers=[self.create_transfer_entry()]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.show_results


class TotalResultsTests(ListTransfersPresenterBase):
    @parameterized.expand(
        [
            (0,),
            (1,),
            (2,),
        ]
    )
    def test_total_results_is_same_as_in_use_case_response(
        self, total_results: int
    ) -> None:
        uc_response = self.create_use_case_response(total_results=total_results)
        view_model = self.presenter.present(uc_response)
        assert view_model.total_results == total_results


class ResultsTests(ListTransfersPresenterBase):
    @parameterized.expand(
        [
            (0,),
            (1,),
            (2,),
        ]
    )
    def test_that_length_of_results_is_same_as_in_use_case_response(
        self, num_results: int
    ) -> None:
        uc_response = self.create_use_case_response(
            transfers=[self.create_transfer_entry() for _ in range(num_results)]
        )
        view_model = self.presenter.present(uc_response)
        assert len(view_model.results.rows) == num_results

    def test_that_transfer_date_is_converted_to_correct_format(self) -> None:
        date = datetime_utc(2023, 1, 1, 10, 30)
        uc_response = self.create_use_case_response(
            transfers=[self.create_transfer_entry(date=date)]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.results.rows[0].date == self.datetime_service.format_datetime(
            date, zone="Europe/Berlin", fmt="%d.%m.%Y %H:%M"
        )

    def test_that_transfer_type_credit_p_is_transfered_to_correct_string(self) -> None:
        uc_response = self.create_use_case_response(
            transfers=[self.create_transfer_entry(transfer_type=TransferType.credit_p)]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.results.rows[0].transfer_type == self.translator.gettext(
            "Credit for fixed means of production"
        )

    def test_that_debit_account_is_converted_to_string(self) -> None:
        original_debit_account = uuid4()
        uc_response = self.create_use_case_response(
            transfers=[self.create_transfer_entry(debit_account=original_debit_account)]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.results.rows[0].debit_account == str(original_debit_account)

    def test_that_credit_account_is_converted_to_string(self) -> None:
        original_credit_account = uuid4()
        uc_response = self.create_use_case_response(
            transfers=[
                self.create_transfer_entry(credit_account=original_credit_account)
            ]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.results.rows[0].credit_account == str(original_credit_account)

    def test_that_none_debit_account_is_converted_to_empty_string(self) -> None:
        uc_response = self.create_use_case_response(
            transfers=[self.create_transfer_entry(debit_account=None)]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.results.rows[0].debit_account == ""

    def test_that_none_credit_account_is_converted_to_empty_string(self) -> None:
        uc_response = self.create_use_case_response(
            transfers=[self.create_transfer_entry(credit_account=None)]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.results.rows[0].credit_account == ""

    def test_that_debtor_name_is_member_if_debtor_is_member(self) -> None:
        uc_response = self.create_use_case_response(
            transfers=[
                self.create_transfer_entry(
                    debtor_type=list_transfers.AccountOwnerType.member
                )
            ]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.results.rows[0].debtor_name == self.translator.gettext(
            "Member"
        )

    def test_that_creditor_name_is_member_if_creditor_is_member(self) -> None:
        uc_response = self.create_use_case_response(
            transfers=[
                self.create_transfer_entry(
                    creditor_type=list_transfers.AccountOwnerType.member
                )
            ]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.results.rows[0].creditor_name == self.translator.gettext(
            "Member"
        )

    def test_that_debtor_name_is_social_accounting_if_debtor_is_social_accounting(
        self,
    ) -> None:
        uc_response = self.create_use_case_response(
            transfers=[
                self.create_transfer_entry(
                    debtor_type=list_transfers.AccountOwnerType.social_accounting
                )
            ]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.results.rows[0].debtor_name == self.translator.gettext(
            "Social Accounting"
        )

    def test_that_creditor_name_is_social_accounting_if_creditor_is_social_accounting(
        self,
    ) -> None:
        uc_response = self.create_use_case_response(
            transfers=[
                self.create_transfer_entry(
                    creditor_type=list_transfers.AccountOwnerType.social_accounting
                )
            ]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.results.rows[0].creditor_name == self.translator.gettext(
            "Social Accounting"
        )

    def test_that_debtor_name_is_company_name(self) -> None:
        expected_debtor_name = "Some company name"
        uc_response = self.create_use_case_response(
            transfers=[
                self.create_transfer_entry(
                    debtor_type=list_transfers.AccountOwnerType.company,
                    debtor_name=expected_debtor_name,
                )
            ]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.results.rows[0].debtor_name == expected_debtor_name

    def test_that_creditor_name_is_company_name(self) -> None:
        expected_creditor_name = "Some company name"
        uc_response = self.create_use_case_response(
            transfers=[
                self.create_transfer_entry(
                    creditor_type=list_transfers.AccountOwnerType.company,
                    creditor_name=expected_creditor_name,
                )
            ]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.results.rows[0].creditor_name == expected_creditor_name

    def test_that_debtor_name_is_cooperation_name(self) -> None:
        expected_debtor_name = "Some cooperation name"
        uc_response = self.create_use_case_response(
            transfers=[
                self.create_transfer_entry(
                    debtor_type=list_transfers.AccountOwnerType.cooperation,
                    debtor_name=expected_debtor_name,
                )
            ]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.results.rows[0].debtor_name == expected_debtor_name

    def test_that_creditor_name_is_cooperation_name(self) -> None:
        expected_creditor_name = "Some cooperation name"
        uc_response = self.create_use_case_response(
            transfers=[
                self.create_transfer_entry(
                    creditor_type=list_transfers.AccountOwnerType.cooperation,
                    creditor_name=expected_creditor_name,
                )
            ]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.results.rows[0].creditor_name == expected_creditor_name

    def test_that_debtor_url_is_none_when_social_accounting_or_member(self) -> None:
        uc_response = self.create_use_case_response(
            transfers=[
                self.create_transfer_entry(
                    debtor_type=list_transfers.AccountOwnerType.social_accounting
                ),
                self.create_transfer_entry(
                    debtor_type=list_transfers.AccountOwnerType.member
                ),
            ]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.results.rows[0].debtor_url is None
        assert view_model.results.rows[1].debtor_url is None

    def test_that_creditor_url_is_none_when_social_accounting_or_member(self) -> None:
        uc_response = self.create_use_case_response(
            transfers=[
                self.create_transfer_entry(
                    creditor_type=list_transfers.AccountOwnerType.social_accounting
                ),
                self.create_transfer_entry(
                    creditor_type=list_transfers.AccountOwnerType.member
                ),
            ]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.results.rows[0].creditor_url is None
        assert view_model.results.rows[1].creditor_url is None

    def test_that_debtor_url_is_company_summary_url(self) -> None:
        debtor = uuid4()
        uc_response = self.create_use_case_response(
            transfers=[
                self.create_transfer_entry(
                    debtor_type=list_transfers.AccountOwnerType.company, debtor=debtor
                )
            ]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.results.rows[
            0
        ].debtor_url == self.url_index.get_company_summary_url(company_id=debtor)

    def test_that_creditor_url_is_company_summary_url(self) -> None:
        creditor = uuid4()
        uc_response = self.create_use_case_response(
            transfers=[
                self.create_transfer_entry(
                    creditor_type=list_transfers.AccountOwnerType.company,
                    creditor=creditor,
                )
            ]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.results.rows[
            0
        ].creditor_url == self.url_index.get_company_summary_url(company_id=creditor)

    def test_that_debtor_url_is_cooperation_summary_url(self) -> None:
        debtor = uuid4()
        uc_response = self.create_use_case_response(
            transfers=[
                self.create_transfer_entry(
                    debtor_type=list_transfers.AccountOwnerType.cooperation,
                    debtor=debtor,
                )
            ]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.results.rows[
            0
        ].debtor_url == self.url_index.get_coop_summary_url(coop_id=debtor)

    def test_that_creditor_url_is_cooperation_summary_url(self) -> None:
        creditor = uuid4()
        uc_response = self.create_use_case_response(
            transfers=[
                self.create_transfer_entry(
                    creditor_type=list_transfers.AccountOwnerType.cooperation,
                    creditor=creditor,
                )
            ]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.results.rows[
            0
        ].creditor_url == self.url_index.get_coop_summary_url(coop_id=creditor)

    @parameterized.expand(
        [
            (Decimal("0"), "0.00"),
            (Decimal("100.499"), "100.50"),
            (Decimal("1000"), "1000.00"),
        ]
    )
    def test_that_transfer_value_is_formatted_correctly(
        self, value: Decimal, expected: str
    ):
        uc_response = self.create_use_case_response(
            transfers=[self.create_transfer_entry(value=value)]
        )
        view_model = self.presenter.present(uc_response)
        assert view_model.results.rows[0].value == expected
