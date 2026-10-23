"""Tests for form validators."""

from unittest.mock import patch

import pytest
from wtforms.validators import ValidationError

from dry_foundation.forms.validators import NumeralsOnly, SelectionNotBlank


@pytest.fixture
def mock_form():
    with patch("flask_wtf.FlaskForm") as mock_form:
        yield mock_form


@pytest.fixture
def mock_field():
    with patch("wtforms.fields.Field") as mock_field:
        yield mock_field


class _TestValidator:
    """Generic base for validator test classes."""

    @staticmethod
    def _ensure_validator_passes(validator, form, field):
        validator(form, field)

    @staticmethod
    def _ensure_validator_raises(validator, form, field, error_match=None):
        with pytest.raises(ValidationError, match=error_match):
            validator(form, field)


class TestNumeralsOnly(_TestValidator):
    """Tests for the ``NumeralsOnly`` validator."""

    @pytest.mark.parametrize("value", ["0", "123", "007"])
    def test_valid_input_numerals_pass(self, mock_form, mock_field, value):
        mock_field.data = value
        self._ensure_validator_passes(NumeralsOnly(), mock_form, mock_field)

    @pytest.mark.parametrize("value", ["abc", "12a", "12.5", "-1", "1_000", ""])
    def test_invalid_input_raises(self, mock_form, mock_field, value):
        mock_field.data = value
        self._ensure_validator_raises(
            NumeralsOnly(),
            mock_form,
            mock_field,
            error_match="Field can only contain numerals",
        )

    def test_custom_message(self, mock_form, mock_field):
        mock_field.data = "abc"
        validator = NumeralsOnly(message="Digits only!")
        assert validator.message == "Digits only!"
        self._ensure_validator_raises(
            validator,
            mock_form,
            mock_field,
            error_match="Digits only!",
        )


class TestSelectionNotBlank(_TestValidator):
    """Tests for the ``SelectionNotBlank`` validator."""

    @pytest.mark.parametrize("value", [0, 1, 2, 3, 1000, "-1"])
    def test_valid_selections_pass(self, mock_form, mock_field, value):
        mock_field.data = value
        self._ensure_validator_passes(SelectionNotBlank(), mock_form, mock_field)

    def test_invalid_default_blank_raises(self, mock_form, mock_field):
        mock_field.data = "-"
        self._ensure_validator_raises(
            SelectionNotBlank(),
            mock_form,
            mock_field,
            error_match="A selection must be made",
        )

    def test_custom_blank_value(self, mock_form, mock_field):
        validator = SelectionNotBlank(blank="")
        assert validator.blank == ""
        # Test that selecting the new custom blank raises the error
        mock_field.data = ""
        self._ensure_validator_raises(
            validator,
            mock_form,
            mock_field,
            error_match="A selection must be made",
        )
        # Test that selecting a choice matching the original blank is now valid
        mock_field.data = "-"
        self._ensure_validator_passes(validator, mock_form, mock_field)

    def test_custom_message(self, mock_form, mock_field):
        mock_field.data = "-"
        validator = SelectionNotBlank(message="Pick one.")
        assert validator.message == "Pick one."
        self._ensure_validator_raises(
            validator,
            mock_form,
            mock_field,
            error_match="Pick one.",
        )
