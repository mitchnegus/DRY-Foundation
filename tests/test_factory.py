"""Tests for the application factory."""

import json
from unittest.mock import Mock, patch

import pytest

from dry_foundation.config.settings import TestingConfig as _TestingConfig
from dry_foundation.factory import DryFlask, Factory


@patch("dry_foundation.factory.Factory.default_db_interface")
def test_factory_decorator_no_args(mock_db_interface):
    mock_factory = Mock()
    decorator = Factory
    # Apply the decorator and check results
    decorated_factory = decorator(mock_factory)
    decorated_factory()
    mock_factory.assert_called_once()
    mock_db_interface.select_interface.assert_called_once()


def test_factory_decorator_with_args():
    mock_factory = Mock()
    mock_db_interface = Mock()
    decorator = Factory(db_interface=mock_db_interface)
    # Apply the decorator and check results
    decorated_factory = decorator(mock_factory)
    decorated_factory()
    mock_factory.assert_called_once()
    mock_db_interface.select_interface.assert_called_once()


class TestDryFlask:
    """Tests for the ``DryFlask`` object."""

    def test_initialize(self):
        app = DryFlask(__name__)
        assert app.app_name == __name__
        assert "dry_foundation" in app.blueprints

    def test_initialize_with_name(self):
        app_name = "Test Application"
        app = DryFlask(__name__, app_name)
        assert app.app_name == app_name

    def test_invalid_application_config(self):
        with pytest.raises(TypeError):
            # This will fail because the `TestingConfig` is not instance-based
            DryFlask.set_default_config_type(_TestingConfig)

    def test_serve_js(self, app, client, client_context):
        js_url = app.url_for("dry_foundation.static", filename="js/modules/requests.js")
        response = client.get(js_url)
        assert response.status_code == 200
        assert "javascript" in response.content_type

    def test_import_map(self, app, client_context):
        map_imports = app.jinja_env.globals.get("map_imports")
        # Confirm the import mapper exists and returns validl JSON
        assert map_imports
        import_map = json.loads(map_imports())
        # Confirm import map has the proper URL
        expected_url = app.url_for(
            "dry_foundation.static", filename="js/modules/requests.js"
        )
        assert import_map["imports"]["dry-foundation/requests"] == expected_url
