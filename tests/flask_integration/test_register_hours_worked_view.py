from .flask import ViewTestCase


class AuthenticatedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()
        self.url = "company/register_hours_worked"

    def test_company_gets_200_when_accessing_page(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_posting_without_data_results_in_400(self) -> None:
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)

    def test_company_gets_302_when_posting_correct_data(self) -> None:
        worker = self.member_generator.create_member()
        self.worker_affiliation_generator.add_workers_to_company(self.company, [worker])
        response = self.client.post(
            self.url,
            data=dict(member_id=str(worker), amount="10"),
        )
        self.assertEqual(response.status_code, 302)

    def test_company_gets_404_when_posting_incorrect_data_with_worker_not_in_company(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        response = self.client.post(
            self.url,
            data=dict(member_id=str(worker), amount="10"),
        )
        self.assertEqual(response.status_code, 404)

    def test_company_gets_400_when_posting_incorrect_data_with_negative_amount(
        self,
    ) -> None:
        worker = self.member_generator.create_member()
        self.worker_affiliation_generator.add_workers_to_company(self.company, [worker])
        response = self.client.post(
            self.url,
            data=dict(member_id=str(worker), amount="-10"),
        )
        self.assertEqual(response.status_code, 400)
