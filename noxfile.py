"""The top-level Nox specification."""

from pathlib import Path

import nox

PACKAGE = "dry_foundation"
PACKAGE_DIR = Path("src", PACKAGE)

#
# --- TESTING ---
#

PYTHON_VERSIONS = ["3.10", "3.11", "3.12"]


@nox.session(name="clean-coverage")
def clean_coverage(session):
    session.install("coverage")
    session.run("coverage", "erase")


@nox.session(name="test", python=PYTHON_VERSIONS, requires=["clean-coverage"])
def test_package(session):
    session.install("-e", ".[test]")
    try:
        session.run("coverage", "run", "-m", "pytest")
    finally:
        session.run("coverage", "report", "--show-missing", "--include", "tests/*")
        session.run("coverage", "report", "--show-missing", "--include", "src/*")
        session.run("coverage", "html")


#
# --- FORMATTING ---
#

FORMAT_DEPS = [
    "black==25.1.0",
    "isort==6.0.1",
]
PYTHON_FORMAT_FILES = ["src/", "tests/", "noxfile.py"]


@nox.session
def format(session):
    session.install(*FORMAT_DEPS)
    session.run("isort", *PYTHON_FORMAT_FILES)
    session.run("black", *PYTHON_FORMAT_FILES)


@nox.session(name="format-diff")
def diff_format(session):
    session.install(*FORMAT_DEPS)
    session.run("isort", "--diff", "--color", *PYTHON_FORMAT_FILES)
    session.run("black", "--diff", "--color", *PYTHON_FORMAT_FILES)


@nox.session(name="format-check")
def check_format(session):
    session.install(*FORMAT_DEPS)
    session.run("isort", "--check", *PYTHON_FORMAT_FILES)
    session.run("black", "--check", *PYTHON_FORMAT_FILES)


#
# --- DOCS ---
#

DOCS_DIR = Path("docs")
DOCS_SRC = DOCS_DIR / "source"
DOCS_SRC_API = DOCS_SRC / "api"
DOCS_BUILD = DOCS_DIR / "build"
DOCS_HTML = DOCS_BUILD / "html"


@nox.session(name="docs")
def build_docs(session):
    session.install("-e", ".[docs]")
    session.run("sphinx-apidoc", "-f", "-o", DOCS_SRC_API, PACKAGE_DIR)
    session.run("sphinx-build", "-b", "html", DOCS_SRC, DOCS_HTML)


#
# --- PACKAGING ---
#

PACKAGING_DEPS = [
    "hatch",
]


@nox.session(name="package")
def build_package(session):
    session.install(*PACKAGING_DEPS)
    session.run("hatch", "build")


@nox.session(name="publish")
def publish_package(session):
    session.install(*PACKAGING_DEPS)
    session.run("hatch", "publish")
