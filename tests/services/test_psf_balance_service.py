from decimal import Decimal
from uuid import UUID

from parameterized import parameterized

from arbeitszeit.interactors.register_hours_worked import (
    RegisterHoursWorkedInteractor,
    RegisterHoursWorkedRequest,
)
from arbeitszeit.services.psf_balance import PublicSectorFundService
from tests.interactors.base_test_case import BaseTestCase


class PublicSectorFundServiceCalculationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.service = self.injector.get(PublicSectorFundService)

    def test_balance_is_zero_if_no_plans_are_approved(self) -> None:
        psf_balance = self.service.calculate_psf_balance()
        self.assertEqual(psf_balance, 0)

    def test_that_balance_is_zero_if_there_is_a_productive_plan_approval(self) -> None:
        self.plan_generator.create_plan()
        psf_balance = self.service.calculate_psf_balance()
        assert psf_balance == Decimal(0)

    def test_that_balance_is_negative_if_there_is_a_public_plan_approval(self) -> None:
        self.plan_generator.create_plan(is_public_service=True)
        psf_balance = self.service.calculate_psf_balance()
        assert psf_balance < Decimal(0)

    def test_that_after_registration_of_hours_worked_balance_is_zero_if_no_plan_approvals(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self._register_hours_worked(company, worker, Decimal(10))
        psf_balance = self.service.calculate_psf_balance()
        assert psf_balance == Decimal(0)

    def test_that_after_registration_of_hours_worked_balance_is_zero_if_only_one_productive_plan_approval(
        self,
    ) -> None:
        self.plan_generator.create_plan()
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self._register_hours_worked(company, worker, Decimal(10))
        psf_balance = self.service.calculate_psf_balance()
        assert psf_balance == Decimal(0)

    @parameterized.expand(
        [
            (Decimal(0), Decimal(1)),
            (Decimal(0.1), Decimal(9)),
            (Decimal(0.5), Decimal(1)),
            (Decimal(0.8), Decimal(0.5)),
        ]
    )
    def test_that_balance_grows_if_payout_factor_is_smaller_than_one_and_worked_hours_are_registered(
        self, payout_factor: Decimal, hours_worked: Decimal
    ) -> None:
        self.economic_scenarios.setup_environment_with_fic(payout_factor)
        psf_balance_before = self.service.calculate_psf_balance()
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self._register_hours_worked(company, worker, hours_worked)
        psf_balance_after = self.service.calculate_psf_balance()
        assert psf_balance_after > psf_balance_before
        self.assertAlmostEqual(
            psf_balance_after, psf_balance_before + (hours_worked * (1 - payout_factor))
        )

    @parameterized.expand(
        [
            (Decimal(10)),
            (Decimal(100)),
            (Decimal(1000)),
        ]
    )
    def test_that_balance_stays_the_same_if_payout_factor_is_one_and_worked_hours_are_registered(
        self, hours_worked: Decimal
    ) -> None:
        fic = Decimal(1)
        self.economic_scenarios.setup_environment_with_fic(fic)
        psf_balance_before = self.service.calculate_psf_balance()
        worker = self.member_generator.create_member()
        company = self.company_generator.create_company(workers=[worker])
        self._register_hours_worked(company, worker, hours_worked)
        psf_balance_after = self.service.calculate_psf_balance()
        assert psf_balance_after == psf_balance_before

    def _register_hours_worked(
        self, company_id: UUID, worker_id: UUID, hours_worked: Decimal
    ) -> None:
        interactor = self.injector.get(RegisterHoursWorkedInteractor)
        response = interactor.execute(
            RegisterHoursWorkedRequest(company_id, worker_id, hours_worked)
        )
        assert not response.is_rejected
