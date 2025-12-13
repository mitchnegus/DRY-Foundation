"""
Objects for building consistent forms.
"""

from abc import ABC, ABCMeta

from flask_wtf import FlaskForm


class _AbstractFlaskFormMeta(ABCMeta, type(FlaskForm)):
    # Defined to allow the `FlaskForm` objects to be abstract base classes
    pass


class AbstractFlaskForm(ABC, FlaskForm, metaclass=_AbstractFlaskFormMeta):
    """An abstract base class representing a ``FlaskForm`` object."""


class FlaskSubform(FlaskForm):
    """A subform disabling CSRF (CSRF is REQUIRED in encapsulating form)."""

    def __init__(self, *args, **kwargs):
        super().__init__(meta={"csrf": False}, *args, **kwargs)
