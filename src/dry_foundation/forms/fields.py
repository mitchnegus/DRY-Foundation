"""
Objects for building consistent form fields.
"""

from abc import ABC, abstractmethod

from wtforms.fields import FieldList, SelectField, SelectMultipleField
from wtforms.utils import unset_value
from wtforms.widgets import CheckboxInput, ListWidget

from .validators import SelectionNotBlank


class DynamicFieldList(FieldList):
    """A field list that can model fields for dynamic extension."""

    def model_extension(self, index, data=unset_value):
        """
        Generate a bound field representing the field at the given index.

        Parameters
        ----------
        index : int
            The index of the field to generate.
        data : dict
            Optional data to pass to the generated field.

        Returns
        -------
        Field
            The field matching the specified index to return.
        """
        # Append dummy data to the entries until reaching the field matching the index
        while (current_max_index := len(self.entries) - 1) < index:
            field_data = unset_value if current_max_index + 1 < index else data
            self.append_entry(data=field_data)
        return self.pop_entry()


class DatabaseSelectField(SelectField, ABC):
    """
    A select field that can auto-prepare choices from the database.

    Parameters
    ----------
    label : str
        The label of the field.
    validators : list or None
        A sequence of validators to call when ``validate`` is called.
    """

    UNSET = "-"

    def __init__(self, label=None, validators=None, **kwargs):
        if validators is None:
            validators = [SelectionNotBlank(blank=self.UNSET)]
        super().__init__(label=label, validators=validators, **kwargs)
        self.prepare_field_choices()

    @property
    def leading_choices(self):
        """Choices that always appear before the database-determined options."""
        return [(self.UNSET, "-")]

    @property
    def trailing_choices(self):
        """Choices that always appear after the database-determined options."""
        return []

    @property
    @abstractmethod
    def _db_repo(self):
        raise NotImplementedError("Define the attribute in a subclass.")

    def process_data(self, value):
        """Process incoming data, and set the field default value."""
        value = self.UNSET if value is None else value
        super().process_data(value)

    def prepare_field_choices(self):
        """
        Prepare choices for a field in the form using the database.

        Using a reference to a database repository, this method queries the
        database for entries belonging to the user, and then uses those
        entries to populate the list of choices that may be selected
        for the field value.
        """
        # Sort database choices for consistency (arbitrarily key by entry ID)
        database_choices = [
            (str(entry.id), self._format_choice(entry))
            for entry in sorted(self._db_repo.get_entries(), key=lambda entry: entry.id)
        ]
        self.choices = [
            *self.leading_choices,
            *database_choices,
            *self.trailing_choices,
        ]

    @abstractmethod
    def _format_choice(self, entry):
        """
        Format a database entry field to display as a form field choice.

        Accepts an entry returned by the database repository, and
        extracts a name to be displayed as a choice in the list of
        choices.
        """
        raise NotImplementedError("Define the formatting for a choice in a subclass.")


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.

    Notes
    -----
    See
    https://wtforms.readthedocs.io/en/3.0.x/specific_problems/#specialty-field-tricks
    for details.
    """

    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class AutocompleteFieldMixin:
    """A mixin class for signifying autocomplete functionality."""

    def __call__(self, *args, **kwargs):
        class_kwarg = kwargs.pop("class_", "") or ""
        css_classes = class_kwarg.split()
        css_classes.append("autocomplete")
        class_ = " ".join(css_classes)
        return super().__call__(*args, class_=class_, **kwargs)


class StrippedFieldMixin:
    """A mixin class for uniformly stripping whitespace from fields."""

    def __init__(self, *args, **kwargs):
        filters = kwargs.pop("filters", [])
        super().__init__(filters=[self._strip_whitespace, *filters], *args, **kwargs)

    @staticmethod
    def _strip_whitespace(value):
        return value.strip() or None if isinstance(value, str) else value
