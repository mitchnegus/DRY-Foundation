"""Tests for forms."""

from abc import abstractmethod
from unittest.mock import patch

import pytest

from dry_foundation.forms import AbstractFlaskForm, FlaskSubform


class MockAbstractForm(AbstractFlaskForm):
    @abstractmethod
    def method(self):
        raise NotImplementedError


class MockValidForm(MockAbstractForm):
    def method(self):
        pass


class MockInvalidForm(MockAbstractForm):
    pass


def test_abstract_form(client_context):
    MockValidForm()
    with pytest.raises(TypeError):
        MockInvalidForm()


def test_subform(client_context):
    with patch.object(FlaskSubform.Meta, "update_values") as mock_meta_update_method:
        FlaskSubform()
        mock_meta_update_method.assert_any_call({"csrf": False})
