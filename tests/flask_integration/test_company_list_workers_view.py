from .flask import ViewTestCase


class ViewTests(ViewTestCase):
    def test_that_company_can_access_worker_list_view(self) -> None:
        company, _, email = self.login_company()
        self.confirm_company(company, email)
        url = "/company/work"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
