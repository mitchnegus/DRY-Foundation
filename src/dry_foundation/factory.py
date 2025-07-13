"""A module defining a generic app factory for creating applications."""

import functools

from flask import Flask

from .cli import interface as cli
from .config import DevelopmentConfig
from .config.default_settings import Config, InstanceBasedConfig
from .database import SQLAlchemy


class DryFlask(Flask):
    """A customized, pre-configured (default instance relative) ``Flask`` object."""

    default_config_type = DevelopmentConfig
    cli_type = None
    import_name = None

    def __init__(
        self, import_name, app_name=None, instance_relative_config=True, **kwargs
    ):
        super().__init__(
            import_name, instance_relative_config=instance_relative_config, **kwargs
        )
        self.app_name = app_name or import_name
        self.cli = cli.DryFlaskGroup(import_name)

    @classmethod
    def set_default_config_type(cls, config_type):
        if not issubclass(config_type, InstanceBasedConfig):
            raise TypeError(
                "The default configuration type must be instance-relative "
                "(specifically a subclass of `InstanceBasedConfig`)."
                f"not {config_type}"
            )
        cls.default_config_type = config_type

    def configure(self, config=None):
        """
        Configure the app based on the provided configuration.
        """
        # Load the default mode configuration when not otherwise specified
        # (including testing)
        config = config or self._build_default_config()
        self.config.from_object(config)

    def _build_default_config(self):
        return self.default_config_type(
            self.import_name, self.instance_path, app_name=self.app_name
        )


class Factory:
    """
    A decorator for application factories that accesses ``DryFlask`` capabilities.
    """

    default_db_interface = SQLAlchemy

    def __init__(self, factory_func=None, /, db_interface=None):
        # The factory function **must** be positional only to identify if this is a
        # decorator with or without arguments
        self._factory_func = factory_func
        self._db_interface_cls = db_interface or self.default_db_interface

    def __call__(self, *args, **kwargs):
        if self._factory_func is not None:
            # Decorator without arguments: return the call to the wrapped function
            return self._call_factory(*args, **kwargs)

        # Decorator with arguments: return the wrapped function
        self._factory_func = args[0]

        @functools.wraps(self._factory_func)
        def _wrapper(*_args, **_kwargs):
            return self._call_factory(*_args, **_kwargs)

        return _wrapper

    def _call_factory(self, *args, **kwargs):
        app = self._factory_func(*args, **kwargs)
        self._db_interface_cls.select_interface(app)
        return app
