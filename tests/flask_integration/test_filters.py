import unittest
from unittest.mock import Mock, patch

from markupsafe import Markup

from arbeitszeit_flask.filters import icon_filter
from tests.flask_integration.flask import ViewTestCase


class TestIconFilter(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.mock_file_reader = Mock()

    def tearDown(self):
        super().tearDown()

    def test_icon_with_default_attributes(self):
        svg_content = '<svg viewBox="0 0 448 512"></svg>'
        self.mock_file_reader.return_value = svg_content

        result = icon_filter("check", reader=self.mock_file_reader)

        expected_output = Markup(
            '<svg data-icon="check" width="24px" height="20px" aria-hidden="true" focusable="false" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"></svg>'
        )
        self.assertEqual(result, expected_output)

    def test_icon_with_custom_attributes(self):
        svg_content = '<svg viewBox="0 0 448 512"></svg>'
        self.mock_file_reader.return_value = svg_content

        attributes = {
            "data-icon": "not-check",
            "data-type": "toggle",
            "class": "foo bar baz",
            "width": "auto",
            "height": "48px",
        }
        result = icon_filter("check", reader=self.mock_file_reader, attrs=attributes)

        expected_output = Markup(
            '<svg data-icon="not-check" width="auto" height="48px" aria-hidden="true" focusable="false" role="img" xmlns="http://www.w3.org/2000/svg" data-type="toggle" class="foo bar baz" viewBox="0 0 448 512"></svg>'
        )
        self.assertEqual(result, expected_output)

    def test_icon_not_found_debug_mode(self):
        self.mock_file_reader.side_effect = FileNotFoundError("File not found")

        with patch.dict("os.environ", {"FLASK_DEBUG": "1"}):
            with self.assertRaises(FileNotFoundError) as context:
                icon_filter("nonexistent", reader=self.mock_file_reader)
            self.assertIn('Icon "nonexistent" not found', str(context.exception))

    def test_icon_not_found_no_debug_mode(self):
        self.mock_file_reader.side_effect = FileNotFoundError("File not found")

        with patch.dict("os.environ", {"FLASK_DEBUG": "0"}):
            result = icon_filter("nonexistent", reader=self.mock_file_reader)
            expected_output = Markup(
                '<!-- An error for "nonexistent" icon occurred -->'
            )
            self.assertEqual(result, expected_output)

    def test_icon_with_no_svg(self):
        svg_content = "<div>No SVG content here</div>"
        self.mock_file_reader.return_value = svg_content

        result = icon_filter("check", reader=self.mock_file_reader)

        expected_output = Markup(
            '<!-- Icon "check" does not contain valid SVG content -->'
        )
        self.assertEqual(result, expected_output)

    def test_unknown_error_debug_mode(self):
        self.mock_file_reader.side_effect = Exception("Some error message")

        with patch.dict("os.environ", {"FLASK_DEBUG": "1"}):
            with self.assertRaises(Exception) as context:
                icon_filter("check", reader=self.mock_file_reader)
            self.assertIn(
                'Error for "check" icon: Some error message', str(context.exception)
            )

    def test_unknown_error_no_debug_mode(self):
        self.mock_file_reader.side_effect = Exception("Some error message")

        with patch.dict("os.environ", {"FLASK_DEBUG": "0"}):
            result = icon_filter("check", reader=self.mock_file_reader)
            expected_output = Markup('<!-- An error for "check" icon occurred -->')
            self.assertEqual(result, expected_output)


class TestIconFilterIntegration(ViewTestCase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_icon_filter_integration(self):
        response = self.client.get("/login-member")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'<svg data-icon="key" width="24px" height="20px" aria-hidden="true" focusable="false" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">\n    <path fill="currentColor" d="M336 352c97.2 0 176-78.8 176-176S433.2 0 336 0S160 78.8 160 176c0 18.7 2.9 36.8 8.3 53.7L7 391c-4.5 4.5-7 10.6-7 17v80c0 13.3 10.7 24 24 24h80c13.3 0 24-10.7 24-24V448h40c13.3 0 24-10.7 24-24V384h40c6.4 0 12.5-2.5 17-7l33.3-33.3c16.9 5.4 35 8.3 53.7 8.3zM376 96a40 40 0 1 1 0 80 40 40 0 1 1 0-80z"/>\n</svg>',
            response.data,
        )
