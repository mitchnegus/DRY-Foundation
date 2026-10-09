"""
Objects for building consistent form fields.
"""

from wtforms.fields import FieldList, SelectMultipleField
from wtforms.utils import unset_value
from wtforms.widgets import CheckboxInput, ListWidget


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


class StrippedFieldMixin:
    """A mixin class for uniformly stripping whitespace from fields."""

    def __init__(self, *args, **kwargs):
        filters = kwargs.pop("filters", [])
        super().__init__(filters=[self._strip_whitespace, *filters], *args, **kwargs)

    @staticmethod
    def _strip_whitespace(value):
        return value.strip() if value else None
