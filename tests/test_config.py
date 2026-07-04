"""Tests for application configuration objects."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from dry_foundation.config import (
    Config,
    DevelopmentConfig,
    ProductionConfig,
)
from dry_foundation.config import (
    TestingConfig as _TestingConfig,  # rename to avoid pytest collection
)

APP_IMPORT_NAME = "test"


@pytest.fixture
def default_config(tmp_path):
    default_config_filepath = tmp_path / "config" / f"{APP_IMPORT_NAME}-config.json"
    default_config_filepath.parent.mkdir()
    default_config_content = {"SECRET_KEY": "test secret key", "OTHER": "other"}
    default_config_filepath.write_text(json.dumps(default_config_content))
    with patch(
        "dry_foundation.config.default_settings.DEFAULT_CONFIG_DIR",
        new=default_config_filepath.parent,
    ):
        yield


@pytest.fixture
def instance_config(instance_path):
    instance_config_filepath = instance_path / "test-config.json"
    instance_config_content = {"OTHER": "test supersede"}
    instance_config_filepath.write_text(json.dumps(instance_config_content))


class TestGenericConfig:
    """Test characteristics of generic configurations."""

    def test_db_path(self):
        config = Config(APP_IMPORT_NAME, db_path="test/path")
        assert config.DATABASE == Path("test/path")

    def test_no_db_path(self):
        config = Config(APP_IMPORT_NAME, db_path=None)
        assert config.DATABASE is None

    def test_invalid_db_path(self):
        with pytest.raises(TypeError):
            Config(APP_IMPORT_NAME, db_path=1)

    def test_preload_data(self):
        # Test a dummy callable for preloading data
        config = Config(APP_IMPORT_NAME, preload_data=lambda _: None)
        assert config.PRELOAD_DATA

    def test_no_preload_data(self):
        config = Config(APP_IMPORT_NAME, preload_data=None)
        assert config.PRELOAD_DATA is None

    def test_preload_data_invalid(self):
        with pytest.raises(TypeError):
            Config(APP_IMPORT_NAME, preload_data="test")

    def test_preload_data_path(self):
        config = Config(APP_IMPORT_NAME, preload_data_path="test/path")
        assert config.PRELOAD_DATA_PATH == Path("test/path")

    def test_no_preload_data_path(self):
        config = Config(APP_IMPORT_NAME, preload_data_path=None)
        assert config.PRELOAD_DATA_PATH is None

    def test_invalid_preload_data_path(self):
        with pytest.raises(TypeError):
            Config(APP_IMPORT_NAME, preload_data_path=1)


class TestProductionConfig:
    """Test the production configuration."""

    def test_initialization(self, instance_path):
        config = ProductionConfig(APP_IMPORT_NAME, instance_path)
        assert config.SECRET_KEY == "INSECURE"

    def test_initialization_default_configuration(self, instance_path, default_config):
        config = ProductionConfig(APP_IMPORT_NAME, instance_path)
        assert config.SECRET_KEY == "test secret key"

    def test_initialization_instance_file_supersedes(
        self,
        instance_path,
        instance_config,
        default_config,
    ):
        config = ProductionConfig(APP_IMPORT_NAME, instance_path)
        assert config.SECRET_KEY == "test secret key"
        assert config.OTHER == "test supersede"


class TestDevelopmentConfig:
    """Test the development configuration."""

    def test_initialization(self, instance_path):
        config = DevelopmentConfig(APP_IMPORT_NAME, instance_path)
        assert config.SECRET_KEY == "development key"
        assert config.PRELOAD_DATA_PATH is None

    def test_default_preload_data_path(self, instance_path):
        # Create (and use by default) a development data spec in the default location
        mock_preload_data_path = instance_path / "dev_data.sql"
        mock_preload_data_path.touch()
        config = DevelopmentConfig(APP_IMPORT_NAME, instance_path)
        assert config.PRELOAD_DATA_PATH == mock_preload_data_path

    def test_preload_data_path(self, tmp_path, instance_path):
        # Create and use a development data spec in an alternate location
        mock_preload_data_path = tmp_path / "test_data.sql"
        mock_preload_data_path.touch()
        config = DevelopmentConfig(
            APP_IMPORT_NAME, instance_path, preload_data_path=mock_preload_data_path
        )
        assert config.PRELOAD_DATA_PATH == mock_preload_data_path


class TestTestingConfig:
    """Test the development configuration."""

    def test_initialization(self):
        mock_db_path = Path("/path/to/test/db.sqlite")
        config = _TestingConfig(APP_IMPORT_NAME, db_path=mock_db_path)
        assert config.SECRET_KEY == "testing key"
        assert config.DATABASE == mock_db_path
        assert config.TESTING is True

    def test_initialization_default_configuration(self, default_config):
        # The global config file should never be consulted during testing
        config = _TestingConfig(APP_IMPORT_NAME)
        assert config.config_filepaths == []

    def test_initialization_custom_configuration(self, tmp_path, default_config):
        custom_path = tmp_path / "custom-test-config.json"
        custom_path.write_text(json.dumps({}))
        config = _TestingConfig(
            APP_IMPORT_NAME,
            custom_config_filepaths=[custom_path],
        )
        assert config.config_filepaths == [custom_path]
