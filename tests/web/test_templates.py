"""Tests for package utilities."""

from datetime import date
from unittest.mock import patch

from dry_foundation.web import define_basic_template_global_variables


@patch("dry_foundation.web.templates.date")
@patch("dry_foundation.web.templates.import_module")
def test_template_global_variables(mock_import_function, mock_date_cls):
    # Set some mock return values
    mock_import_function.return_value.version = "M.m.p.devX"
    mock_date_cls.today.return_value = date(2000, 1, 1)
    # Check the variable values
    template_global_variables = define_basic_template_global_variables("module.name")
    assert template_global_variables == {
        "app_version": "M.m.p.devX",
        "copyright_statement": "© 2000",
        "date_today": date(2000, 1, 1),
    }


@patch("dry_foundation.web.templates.import_module")
def test_template_global_variables_invalid_version_module(mock_import_function):
    mock_import_function.side_effect = ModuleNotFoundError
    template_global_variables = define_basic_template_global_variables("module.name")
    assert template_global_variables["app_version"] == ""


@patch("dry_foundation.web.templates.import_module")
def test_template_global_variables_hashed_version(mock_import_function):
    mock_import_function.return_value.version = "M.m.p.devX+abcdef"
    template_global_variables = define_basic_template_global_variables("module.name")
    assert template_global_variables["app_version"] == "M.m.p.devX"
