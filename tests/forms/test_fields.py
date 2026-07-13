"""Tests for form fields."""

import pytest
from flask_wtf import FlaskForm
from wtforms.fields import StringField

from dry_foundation.forms.fields import DynamicFieldList


class SampleForm(FlaskForm):
    items = DynamicFieldList(StringField())


@pytest.fixture
def sample_form():
    return SampleForm()


class TestDynamicFieldList:
    """Tests for the ``DynamicFieldList`` object."""

    def test_model_extension(self, client_context, sample_form):
        field_data = {"test": "data"}
        result_field = sample_form.items.model_extension(2, data=field_data)
        assert isinstance(result_field, StringField)
        assert result_field.data == field_data
        assert all(isinstance(_, StringField) for _ in sample_form.items.entries)
