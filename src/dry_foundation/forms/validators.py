"""
Commonly shared form validators.
"""

from wtforms.validators import ValidationError


class NumeralsOnly:
    """
    Validates text contains only numerals.

    Parameters
    ----------
    message : str
        Error message to raise in case of a validation error.
    """

    def __init__(self, message=None):
        self.message = message or "Field can only contain numerals"

    def __call__(self, form, field):
        if not str(field.data).isdigit():
            raise ValidationError(self.message)


class SelectionNotBlank:
    """
    Validates that a selection is not a blank submission.

    Parameters
    ----------
    blank :
        The value representing a blank selection. The default is the
        dash (``-``).
    message : str
        Error message to raise in case of a validation error.
    """

    def __init__(self, blank="-", message=None):
        self.blank = blank
        self.message = message or "A selection must be made"

    def __call__(self, form, field):
        if field.data == self.blank:
            raise ValidationError(self.message)
