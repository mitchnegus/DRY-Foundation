"""Tests for package utilities."""

from datetime import datetime
from unittest.mock import patch

from dry_foundation.utils import get_timestamp


@patch("dry_foundation.utils.datetime")
def test_get_timestamp(mock_datetime_cls):
    mock_datetime_cls.now.return_value = datetime(2000, 1, 2, 3, 4, 5)
    assert get_timestamp() == "20000102_030405"
