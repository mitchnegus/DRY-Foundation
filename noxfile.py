"""The top-level Nox specification."""

import nox

# env_list = ['clean', '3.9', '3.10', '3.11', '3.12', '3.13']
#
# [env_run_base]
# description = 'Run tests for the package'
# extras = ['test']
# commands = [
#  ['coverage', 'run', '--source={env_site_packages_dir}/dry_foundation', '-m', 'pytest'],
#  ['coverage', { replace = 'posargs', default = ['report'], extend = true }],
# ]
#
# [env.clean]
# deps = ['coverage[toml]']
# skip_install = true
# commands = [ ['coverage', 'erase'] ]

#
# --- TESTING ---
#

TESTING_DEPS = [
    "coverage[toml]==7.6.10",
    "pytest==8.3.4",
]
PYTHON_VERSIONS = ["3.10"]  # , "3.11", "3.12", "3.13"]


@nox.session(name="test", python=PYTHON_VERSIONS)
def test_package(session):
    session.install(*TESTING_DEPS, "-e", ".")
    # session.run("coverage", "run", "--source=src/dry_foundation", "-m", "pytest")
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
