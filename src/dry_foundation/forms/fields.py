"""
Objects for building consistent form fields.
"""

from wtforms.fields import FieldList
from wtforms.utils import unset_value


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
