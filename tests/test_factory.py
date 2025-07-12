"""Tests for the application factory."""

import pytest

from dry_foundation.config.settings import TestingConfig as _TestingConfig
from dry_foundation.factory import DryFlask


def test_invalid_application_config():
    with pytest.raises(TypeError):
        # This will fail because the `TestingConfig` is not instance-based
        DryFlask.set_default_config_type(_TestingConfig)
