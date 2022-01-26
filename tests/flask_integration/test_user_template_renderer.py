from arbeitszeit_flask.template import UserTemplateRenderer
from tests.data_generators import CompanyGenerator
from tests.session import FakeSession

from .flask import FlaskTestCase
from .renderer import FakeTemplateRenderer


class CompanyTemplateRendererTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.fake_template_renderer = FakeTemplateRenderer()
        self.session = FakeSession()
        self.renderer = self.injector.create_object(
            UserTemplateRenderer,
            additional_kwargs=dict(
                inner_renderer=self.fake_template_renderer, session=self.session
            ),
        )
        self.company_generator = self.injector.get(CompanyGenerator)

    def test_renders_templates_without_content(self) -> None:
        expected_content = "test content"
        self.fake_template_renderer.register_template(
            name="test.html", content=expected_content
        )
        rendered = self.renderer.render_template("test.html")
        self.assertEqual(rendered, expected_content)

    def test_renders_templates_with_proper_context(self) -> None:
        self.fake_template_renderer.register_template(name="test.html")
        self.renderer.render_template(
            "test.html", context={"test variable": "test value"}
        )
        self.assertIn(
            "test variable",
            self.fake_template_renderer.previouse_render_context,
        )

    def test_addes_message_indicator_to_context_when_user_is_registered(self) -> None:
        self.fake_template_renderer.register_template(name="test.html")
        user = self.company_generator.create_company()
        self.session.set_current_user_id(user.id)
        self.renderer.render_template("test.html")
        self.assertIn(
            "message_indicator", self.fake_template_renderer.previouse_render_context
        )
