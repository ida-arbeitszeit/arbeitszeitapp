from unittest import TestCase

from project.template import CompanyTemplateIndex, MemberTemplateIndex


class MemberIndexTests(TestCase):
    def setUp(self) -> None:
        self.index = MemberTemplateIndex()

    def test_that_template_resolves_to_correct_path(self) -> None:
        template = self.index.get_template_by_name("test_template")
        self.assertEqual(template, "member/test_template.html")


class CompanyIndexTests(TestCase):
    def setUp(self) -> None:
        self.index = CompanyTemplateIndex()

    def test_that_template_resolves_to_correct_path(self) -> None:
        template = self.index.get_template_by_name("test_template")
        self.assertEqual(template, "company/test_template.html")
