from arbeitszeit_web.prepare_strings_for_html import text_to_html
from flask import Markup


def test_that_flask_markup_object_is_returned():
    output = text_to_html("some text")
    assert isinstance(output, Markup)


def test_that_non_dangerous_chars_are_not_changed():
    input = """no dangerous characters’"'1234567890äöüzy"""
    output = text_to_html(input)
    assert input == output


def test_that_dangerous_chars_are_replaced():
    input = "test < test > test &"
    output = text_to_html(input)
    assert output == "test &lt; test &gt; test &amp;"


def test_that_carriage_return_and_line_feed_are_changed_to_line_break():
    input = "test\r\rtest\rtest\n\ntest\ntest\r\ntest"
    output = text_to_html(input)
    assert output == "test<br><br>test<br>test<br><br>test<br>test<br>test"
