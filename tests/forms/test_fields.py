"""Tests for form fields."""

import pytest
from flask_wtf import FlaskForm
from werkzeug.datastructures import MultiDict
from wtforms.fields import StringField

from dry_foundation.forms.fields import DynamicFieldList, StrippedFieldMixin


class DynamicFieldListSampleForm(FlaskForm):
    items = DynamicFieldList(StringField())


class TestDynamicFieldList:
    """Tests for the ``DynamicFieldList`` object."""

    @pytest.fixture
    def sample_form(self, client_context):
        return DynamicFieldListSampleForm()

    def test_model_extension(self, sample_form):
        field_data = {"test": "data"}
        result_field = sample_form.items.model_extension(2, data=field_data)
        assert isinstance(result_field, StringField)
        assert result_field.data == field_data
        assert all(isinstance(_, StringField) for _ in sample_form.items.entries)


class StrippedStringTestField(StrippedFieldMixin, StringField):
    pass


class StrippedStringTestForm(FlaskForm):
    string = StrippedStringTestField("Test Field")


class TestStrippedFieldMixin:
    """Tests for the ``StrippedFieldMixin`` object."""

    @pytest.fixture
    def sample_form(self, client_context):
        return StrippedStringTestForm()

    @pytest.mark.parametrize(
        ("raw_string", "processed_string"),
        [
            ("non-whitespace string", "non-whitespace string"),
            ("  whitespace string  ", "whitespace string"),
        ],
    )
    def test_stripped_field(self, sample_form, raw_string, processed_string):
        test_formdata = MultiDict([("string", raw_string)])
        sample_form.process(formdata=test_formdata)
        assert sample_form.string.data == processed_string
