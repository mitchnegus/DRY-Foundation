"""Helper objects to improve the modularity of tests."""

from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, mapped_column

from dry_foundation import DryFlask, Factory
from dry_foundation.database import SQLAlchemy


@Factory(SQLAlchemy)
def create_test_app(config=None):
    # Create and configure the test app
    app = DryFlask("test", "Test Application")
    app.configure(config)
    return app


class Base(DeclarativeBase):
    metadata = SQLAlchemy.metadata


class Entry(Base):
    __tablename__ = "entries"
    # Columns
    x = mapped_column(Integer, primary_key=True)
    y = mapped_column(String, nullable=False)
    user_id = mapped_column(Integer, nullable=False)
