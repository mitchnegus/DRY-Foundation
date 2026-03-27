"""The top-level Nox specification."""

import nox

#
# --- TESTING ---
#


@nox.session(name="clean-coverage")
def clean_coverage(session):
    session.install("coverage")
    session.run("coverage", "erase")


@nox.session(
    name="test",
    venv_backend="uv",
    python=["3.10", "3.11", "3.12", "3.13"],
    requires=["clean-coverage"],
)
def test_package(session):
    session.run_install(
        "uv",
        "sync",
        "--quiet",
        "--group=test",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
        external=True,
    )
    try:
        session.run("coverage", "run", "-m", "pytest")
    finally:
        session.run("coverage", "report", "--show-missing", "--include", "tests/*")
        session.run("coverage", "report", "--show-missing", "--include", "src/*")
        session.run("coverage", "html")
