from arbeitszeit_flask.template import CompanyTemplateIndex, MemberTemplateIndex

from .flask import FlaskTestCase


class MemberIndexTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.index = MemberTemplateIndex()

    def test_that_template_resolves_to_correct_path(self) -> None:
        template = self.index.get_template_by_name("test_template")
        self.assertEqual(template, "member/test_template.html")


class CompanyIndexTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.index = CompanyTemplateIndex()

    def test_that_template_resolves_to_correct_path(self) -> None:
        template = self.index.get_template_by_name("test_template")
        self.assertEqual(template, "company/test_template.html")
