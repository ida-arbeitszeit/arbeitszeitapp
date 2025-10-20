import unittest
from unittest.mock import Mock

from markupsafe import Markup

from arbeitszeit_flask.filters import icon_filter
from tests.flask_integration.base_test_case import ViewTestCase


class IconFilterUnitTests(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.mock_file_reader = Mock()

    def test_that_icon_filter_returns_empty_string_for_empty_icon_name(
        self,
    ):
        valid_icon_template_content = (
            '<svg viewBox="0 0 448 512"><!-- no path to keep it short --></svg>'
        )
        self.mock_file_reader.return_value = valid_icon_template_content

        result = icon_filter(icon_name="", reader=self.mock_file_reader)

        expected_output = ""
        self.assertEqual(result, expected_output)

    def test_that_icon_filter_returns_empty_string_for_whitespace_icon_name(
        self,
    ):
        valid_icon_template_content = (
            '<svg viewBox="0 0 448 512"><!-- no path to keep it short --></svg>'
        )
        self.mock_file_reader.return_value = valid_icon_template_content

        empty_like = "             "

        result = icon_filter(icon_name=empty_like, reader=self.mock_file_reader)

        expected_output = ""
        self.assertEqual(result, expected_output)

    def test_that_icon_filter_raises_exception_for_invalid_template(
        self,
    ):
        non_valid_icon_template_content = "<div>No SVG content here</div>"
        self.mock_file_reader.return_value = non_valid_icon_template_content

        with self.assertRaises(Exception) as context:
            icon_filter(icon_name="test-name", reader=self.mock_file_reader)
            self.assertIn(
                'Exception for "test-name" icon: Icon "test-name" does not contain valid SVG content: <div>No SVG content here</div>',
                str(context.exception),
            )

    def test_that_icon_filter_transforms_valid_template_to_html_svg_with_default_attributes(
        self,
    ):
        valid_icon_template_content = (
            '<svg viewBox="0 0 448 512"><!-- no path to keep it short --></svg>'
        )
        self.mock_file_reader.return_value = valid_icon_template_content

        result = icon_filter(icon_name="test-name", reader=self.mock_file_reader)

        expected_output = Markup(
            '<svg data-icon="test-name" width="24px" height="20px" aria-hidden="true" focusable="false" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><!-- no path to keep it short --></svg>'
        )
        self.assertEqual(result, expected_output)

    def test_that_icon_filter_transforms_template_to_html_svg_with_custom_attributes(
        self,
    ):
        svg_content = (
            '<svg viewBox="0 0 448 512"><!-- no path to keep it short --></svg>'
        )
        self.mock_file_reader.return_value = svg_content

        attributes = {
            "data-icon": "not-test-name",  # overwrite
            "data-type": "toggle",  # new
            "class": "foo bar baz",  # new
            "width": "auto",  # overwrite
            "height": "48px",  # overwrite
        }
        result = icon_filter(
            icon_name="test-name", reader=self.mock_file_reader, attrs=attributes
        )

        expected_output = Markup(
            '<svg data-icon="not-test-name" width="auto" height="48px" aria-hidden="true" focusable="false" role="img" xmlns="http://www.w3.org/2000/svg" data-type="toggle" class="foo bar baz" viewBox="0 0 448 512"><!-- no path to keep it short --></svg>'
        )
        self.assertEqual(result, expected_output)

    def test_that_icon_filter_passes_enriched_file_not_found_error(
        self,
    ):
        self.mock_file_reader.side_effect = FileNotFoundError("File not found")

        with self.assertRaises(FileNotFoundError) as context:
            icon_filter(icon_name="nonexistent", reader=self.mock_file_reader)

            self.assertIn(
                'Error for "nonexistent" icon: File not found', str(context.exception)
            )

    def test_that_icon_filter_passes_generic_exception(self):
        self.mock_file_reader.side_effect = Exception("Some error message")

        with self.assertRaises(Exception) as context:
            icon_filter(icon_name="test-name", reader=self.mock_file_reader)
            self.assertIn(
                'Exception for "test-name" icon: Some error message',
                str(context.exception),
            )


class IconFilterIntegrationTest(ViewTestCase):
    def test_that_icon_filter_renders_a_valid_key_icon_svg_element_in_the_login_form_on_page_load(
        self,
    ):
        response = self.client.get("/login-member")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'<svg data-icon="key" width="24px" height="20px" aria-hidden="true" focusable="false" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">\n    <path fill="currentColor" d="M336 352c97.2 0 176-78.8 176-176S433.2 0 336 0S160 78.8 160 176c0 18.7 2.9 36.8 8.3 53.7L7 391c-4.5 4.5-7 10.6-7 17v80c0 13.3 10.7 24 24 24h80c13.3 0 24-10.7 24-24V448h40c13.3 0 24-10.7 24-24V384h40c6.4 0 12.5-2.5 17-7l33.3-33.3c16.9 5.4 35 8.3 53.7 8.3zM376 96a40 40 0 1 1 0 80 40 40 0 1 1 0-80z"/>\n</svg>',
            response.data,
        )
