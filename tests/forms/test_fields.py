"""Tests for form fields."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest
from flask_wtf import FlaskForm
from werkzeug.datastructures import MultiDict
from wtforms.fields import StringField
from wtforms.validators import DataRequired

from dry_foundation.forms.fields import (
    AutocompleteFieldMixin,
    DatabaseSelectField,
    DynamicFieldList,
    MultiCheckboxField,
    StrippedFieldMixin,
)


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


class SampleRepo:
    """A stand in for a database repository."""

    def get_entries():
        raise NotImplementedError


class DatabaseSelectTestField(DatabaseSelectField):
    _db_repo = SampleRepo()

    def _format_choice(self, entry):
        return entry.name


class DatabaseSelectFieldSampleForm(FlaskForm):
    selection = DatabaseSelectTestField("Selection")


class CustomValidatorDatabaseSelectFieldSampleForm(FlaskForm):
    selection = DatabaseSelectTestField("Selection", validators=[DataRequired()])


class TestDatabaseSelectField:
    """Tests for the ``DatabaseSelectField`` object."""

    @staticmethod
    def _get_custom_sample_form_patch(entry_ids=[]):
        entries = [SimpleNamespace(id=id_, name=f"Entry {id_}") for id_ in entry_ids]
        return patch.object(SampleRepo, "get_entries", return_value=entries)

    def _customize_sample_form(self, entry_ids):
        with self._get_custom_sample_form_patch(entry_ids):
            return DatabaseSelectFieldSampleForm()

    @pytest.fixture
    def sample_form(self, client_context):
        return self._customize_sample_form([1, 2])

    def test_abstract_field_cannot_be_instantiated(self, client_context):
        class IncompleteField(DatabaseSelectField):
            pass  # missing `_db_repo` and `_format_choice`

        class IncompleteForm(FlaskForm):
            item = IncompleteField("Item")

        with pytest.raises(TypeError):
            IncompleteForm()

    @pytest.mark.parametrize(
        ("entry_ids", "expected_choices"),
        [
            ((), [("-", "-")]),
            ((1, 2), [("-", "-"), ("1", "Entry 1"), ("2", "Entry 2")]),
            (  # Entries should be sorted by their actual ID, not by string value
                (10, 2, 1),
                [("-", "-"), ("1", "Entry 1"), ("2", "Entry 2"), ("10", "Entry 10")],
            ),
        ],
    )
    def test_prepare_field_choices(self, client_context, entry_ids, expected_choices):
        form = self._customize_sample_form(entry_ids)
        assert form.selection.choices == expected_choices

    def test_blank_choice_first(self, sample_form):
        assert sample_form.selection.choices[0] == (DatabaseSelectField.UNSET, "-")

    def test_choices_refresh_on_instantiation(self, client_context):
        with self._get_custom_sample_form_patch(entry_ids=[1]):
            first_form = DatabaseSelectFieldSampleForm()
        with self._get_custom_sample_form_patch(entry_ids=[1, 2]):
            second_form = DatabaseSelectFieldSampleForm()
        assert len(first_form.selection.choices) == 2
        assert len(second_form.selection.choices) == 3

    def test_process_data_default(self, sample_form):
        sample_form.process()
        assert sample_form.selection.data == DatabaseSelectField.UNSET

    def test_process_data_coerces_to_string(self, sample_form):
        sample_form.process(data={"selection": 2})
        assert sample_form.selection.data == "2"

    def test_default_validator_rejects_blank(self, sample_form):
        formdata = MultiDict([("selection", DatabaseSelectField.UNSET)])
        sample_form.process(formdata=formdata)
        assert not sample_form.selection.validate(sample_form)
        assert sample_form.selection.errors

    def test_valid_selection(self, sample_form):
        formdata = MultiDict([("selection", "2")])
        sample_form.process(formdata=formdata)
        assert sample_form.selection.validate(sample_form)

    @pytest.mark.parametrize(
        "selection",
        [
            DatabaseSelectField.UNSET,  # the default validator rejects blank selections
            "99",
        ],
    )
    def test_selection_not_in_choices(self, sample_form, selection):
        formdata = MultiDict([("selection", selection)])
        sample_form.process(formdata=formdata)
        assert not sample_form.selection.validate(sample_form)
        assert sample_form.selection.errors

    def test_custom_validators_replace_default(self, client_context):
        # Documents current behavior: the blank check is not applied
        with self._get_custom_sample_form_patch([1]):
            form = CustomValidatorDatabaseSelectFieldSampleForm()
        form.process(formdata=MultiDict([("selection", DatabaseSelectField.UNSET)]))
        assert form.selection.validate(form)


class MultiCheckboxFieldSampleForm(FlaskForm):
    choices = [
        ("thing-one", "Thing 1"),
        ("thing-two", "Thing 2"),
        ("thing-three", "Thing 3"),
    ]
    selections = MultiCheckboxField("Selections", choices=choices)


class TestMultiCheckboxField:
    """Tests for the ``MultiCheckboxField`` object."""

    @pytest.fixture
    def sample_form(self, client_context):
        return MultiCheckboxFieldSampleForm()

    def test_multi_checkbox_field(self, sample_form):
        test_formdata = MultiDict(
            [
                ("selections", "thing-one"),
                ("selections", "thing-two"),
            ]
        )
        sample_form.process(formdata=test_formdata)
        assert sample_form.selections.data == ["thing-one", "thing-two"]


class AutocompleteTestField(AutocompleteFieldMixin, StringField):
    pass


class AutocompleteTestForm(FlaskForm):
    string = AutocompleteTestField("Test field")


class TestAutocompleteFieldMixin:
    """Tests for the ``AutocompleteFieldMixin`` object."""

    @pytest.fixture
    def sample_form(self, client_context):
        return AutocompleteTestForm()

    @pytest.mark.parametrize(
        ("given_class", "expected_class"),
        [
            (None, "autocomplete"),
            ("test", "test autocomplete"),
        ],
    )
    def test_autocomplete_field(self, sample_form, given_class, expected_class):
        with patch.object(StringField, "__call__") as call_method:
            sample_form.string(class_=given_class)
        call_method.assert_called_once_with(class_=expected_class)


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
