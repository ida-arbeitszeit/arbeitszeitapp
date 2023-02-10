import os.path as path
from typing import List

from arbeitszeit.injector import Binder, CallableProvider, Module
from arbeitszeit_flask.template import FlaskTemplateRenderer

from ..dependency_injection import FlaskConfiguration
from ..flask import FlaskTestCase


class FlaskTemplateRendererTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.renderer = self.injector.get(FlaskTemplateRenderer)

    def get_injection_modules(self) -> List[Module]:
        return [FlaskModule()]

    def test_renderer_finds_templates_when_rendering(self) -> None:
        result = self.renderer.render_template("test.html")
        self.assertEqual(result, "test content")

    def test_renderer_provides_context_when_rendering(self) -> None:
        result = self.renderer.render_template(
            "template_with_context.html", context={"test_variable": "test_value"}
        )
        self.assertEqual(result, "test_value")


class FlaskModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[FlaskConfiguration] = CallableProvider(
            FlaskModule.provide_flask_configuration, is_singleton=True
        )

    @staticmethod
    def provide_flask_configuration() -> FlaskConfiguration:
        config = FlaskConfiguration.default()
        config.template_folder = path.dirname(__file__)
        return config
