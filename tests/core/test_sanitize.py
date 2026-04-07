"""Tests for neuraprop_core.sanitize — input sanitization utilities."""

import pytest

from neuraprop_core.sanitize import (
    sanitize_html,
    strip_control_chars,
    sanitize_text_input,
    sanitize_identifier,
    check_path_traversal,
    sanitize_filename,
    mask_sensitive,
    sanitize_log_value,
)


class TestSanitizeHtml:
    def test_escapes_angle_brackets(self):
        assert sanitize_html("<script>alert('xss')</script>") == (
            "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
        )

    def test_escapes_quotes(self):
        assert sanitize_html('a "b" c') == "a &quot;b&quot; c"

    def test_escapes_ampersand(self):
        assert sanitize_html("a & b") == "a &amp; b"

    def test_passes_safe_text(self):
        assert sanitize_html("Hello world") == "Hello world"


class TestStripControlChars:
    def test_removes_null_bytes(self):
        assert strip_control_chars("hello\x00world") == "helloworld"

    def test_preserves_newlines_and_tabs(self):
        assert strip_control_chars("hello\n\tworld") == "hello\n\tworld"

    def test_removes_bell_and_backspace(self):
        assert strip_control_chars("abc\x07\x08def") == "abcdef"

    def test_removes_delete_char(self):
        assert strip_control_chars("abc\x7fdef") == "abcdef"


class TestSanitizeTextInput:
    def test_strips_whitespace(self):
        assert sanitize_text_input("  hello  ") == "hello"

    def test_strips_control_chars(self):
        assert sanitize_text_input("hello\x00world") == "helloworld"

    def test_truncates_to_max_length(self):
        result = sanitize_text_input("a" * 200, max_length=100)
        assert len(result) == 100

    def test_default_max_length(self):
        result = sanitize_text_input("a" * 20000)
        assert len(result) == 10000


class TestSanitizeIdentifier:
    def test_allows_alphanumeric(self):
        assert sanitize_identifier("hello123") == "hello123"

    def test_allows_hyphens_and_underscores(self):
        assert sanitize_identifier("hello-world_123") == "hello-world_123"

    def test_removes_special_characters(self):
        assert sanitize_identifier("hello!@#$%^&*()world") == "helloworld"

    def test_removes_spaces(self):
        assert sanitize_identifier("hello world") == "helloworld"

    def test_removes_sql_chars(self):
        assert sanitize_identifier("name'; DROP TABLE--") == "nameDROPTABLE--"


class TestCheckPathTraversal:
    def test_detects_dot_dot_slash(self):
        assert check_path_traversal("../../../etc/passwd") is True

    def test_detects_backslash_traversal(self):
        assert check_path_traversal("..\\..\\etc\\passwd") is True

    def test_detects_url_encoded_traversal(self):
        assert check_path_traversal("%2e%2e/etc/passwd") is True

    def test_allows_normal_paths(self):
        assert check_path_traversal("documents/report.pdf") is False

    def test_allows_single_dot(self):
        assert check_path_traversal("./file.txt") is False


class TestSanitizeFilename:
    def test_removes_path_separators(self):
        result = sanitize_filename("path/to/file.txt")
        assert "/" not in result

    def test_removes_backslashes(self):
        result = sanitize_filename("path\\to\\file.txt")
        assert "\\" not in result

    def test_replaces_special_chars(self):
        result = sanitize_filename("file name (1).txt")
        assert " " not in result
        assert "(" not in result

    def test_limits_length(self):
        result = sanitize_filename("a" * 300 + ".pdf")
        assert len(result) <= 255

    def test_preserves_extension(self):
        result = sanitize_filename("document.pdf")
        assert result == "document.pdf"


class TestMaskSensitive:
    def test_masks_api_key(self):
        result = mask_sensitive("np_live_alpha_abc123")
        assert result.endswith("c123")
        assert result.startswith("•")
        assert "np_live" not in result

    def test_masks_short_value(self):
        result = mask_sensitive("ab", visible_chars=4)
        assert result == "••"

    def test_custom_visible_chars(self):
        result = mask_sensitive("abcdefghij", visible_chars=6)
        # len=10, visible=6, masked=4
        assert result == "••••efghij"


class TestSanitizeLogValue:
    def test_masks_api_keys(self):
        result = sanitize_log_value("np_live_testfirm_abc123")
        assert "np_live" not in result
        assert "•" in result

    def test_masks_jwt_tokens(self):
        result = sanitize_log_value("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test")
        assert "eyJhbG" not in result

    def test_truncates_long_strings(self):
        result = sanitize_log_value("x" * 600)
        assert len(result) < 600
        assert "truncated" in result

    def test_passes_normal_values(self):
        assert sanitize_log_value("hello") == "hello"
        assert sanitize_log_value(42) == 42
        assert sanitize_log_value(None) is None
