from typing import Dict, List

from injector import Module, provider

from arbeitszeit_flask.template import AnonymousUserTemplateRenderer, TemplateRenderer
from tests.language_service import FakeLanguageService

from .dependency_injection import FlaskConfiguration
from .flask import FlaskTestCase
from .renderer import FakeTemplateRenderer


class CompanyTemplateRendererTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.fake_template_renderer = self.injector.get(FakeTemplateRenderer)
        self.language_service = self.injector.get(FakeLanguageService)
        self.renderer = self.injector.get(
            AnonymousUserTemplateRenderer,
        )

    def test_that_template_is_properly_rendered(self) -> None:
        expected_content = "test content"
        self.fake_template_renderer.register_template(
            name="test.html", content=expected_content
        )
        rendered = self.renderer.render_template("test.html", context={})
        self.assertEqual(rendered, expected_content)

    def test_that_context_variables_are_passed_to_template(self) -> None:
        expected_variable = "test variable"
        self.fake_template_renderer.register_template(name="test.html")
        self.renderer.render_template("test.html", context={expected_variable: ""})
        self.assertIn(
            expected_variable, self.fake_template_renderer.previous_render_context
        )

    def test_that_languages_variable_is_in_context(self) -> None:
        self.fake_template_renderer.register_template(name="test.html")
        self.renderer.render_template("test.html", context={})
        self.assertIn("languages", self.fake_template_renderer.previous_render_context)

    def test_that_language_context_contains_proper_language_codes(self) -> None:
        self.fake_template_renderer.register_template(name="test.html")
        self.renderer.render_template("test.html", context={})
        language_context = self.fake_template_renderer.previous_render_context[
            "languages"
        ]
        self.assertEqual(len(language_context.languages_listing), 3)

    @property
    def expected_languages(self) -> Dict[str, str]:
        return {
            "lang1": "lang1",
            "lang2": "lang2",
            "lang3": "lang3",
        }

    def get_injection_modules(self) -> List[Module]:
        expected_languages = self.expected_languages

        class _Module(Module):
            @provider
            def provide_flask_configuration(self) -> FlaskConfiguration:
                configuration = FlaskConfiguration.default()
                configuration["LANGUAGES"] = expected_languages
                return configuration

            @provider
            def provide_template_renderer(
                self, template_renderer: FakeTemplateRenderer
            ) -> TemplateRenderer:
                return template_renderer

        modules = super().get_injection_modules()
        modules.append(_Module())
        return modules
