"""Tests for the web response infrastructure."""

import pytest

from dry_foundation.web import fetch_json_envelope


@pytest.fixture(scope="module")
def mock_app(app_test_manager):
    with app_test_manager.app_test_context("ephemeral_app"):
        app = app_test_manager.get_app()

        @app.route("/html-only")
        @fetch_json_envelope
        def html_only():
            return "<div>hello</div>"

        @app.route("/html-with-status")
        @fetch_json_envelope
        def html_with_status():
            return "<div>created</div>", 201

        @app.route("/html-with-headers")
        @fetch_json_envelope
        def html_with_headers():
            return "<div>tagged</div>", {"X-Custom-Header": "value"}

        @app.route("/html-with-status-and-headers")
        @fetch_json_envelope
        def html_with_status_and_headers():
            return "<div>full</div>", 202, {"X-Custom-Header": "value"}

        @app.route("/empty-html")
        @fetch_json_envelope
        def empty_html():
            return ""

        @app.route("/non-string-body")
        @fetch_json_envelope
        def non_string_body():
            return {"not": "a string"}, 200

        yield app


class TestJSONEnvelope:
    """Test the decorator for building JSON envelopes for HTML responses."""

    def test_plain_string_response_is_wrapped_as_json(self, client, mock_app):
        response = client.get("/html-only")
        assert response.status_code == 200
        assert response.content_type == "application/json"
        assert response.get_json() == {"type": "html", "content": "<div>hello</div>"}

    def test_string_and_status_tuple_preserves_status(self, client):
        response = client.get("/html-with-status")
        assert response.status_code == 201
        assert response.get_json() == {"type": "html", "content": "<div>created</div>"}

    def test_string_and_headers_tuple_preserves_headers(self, client):
        response = client.get("/html-with-headers")
        assert response.status_code == 200
        assert response.headers.get("X-Custom-Header") == "value"
        assert response.get_json() == {"type": "html", "content": "<div>tagged</div>"}

    def test_string_status_and_headers_tuple_preserves_both(self, client):
        response = client.get("/html-with-status-and-headers")
        assert response.status_code == 202
        assert response.headers.get("X-Custom-Header") == "value"
        assert response.get_json() == {"type": "html", "content": "<div>full</div>"}

    def test_empty_string_response_is_wrapped(self, client):
        response = client.get("/empty-html")
        assert response.status_code == 200
        assert response.get_json() == {"type": "html", "content": ""}

    def test_response_content_type_is_always_json(self, client):
        for path in ("/html-only", "/html-with-status", "/html-with-headers"):
            response = client.get(path)
            assert response.content_type == "application/json"

    def test_non_string_body_raises_type_error(self, client):
        with pytest.raises(TypeError, match="must return a string"):
            client.get("/non-string-body")
