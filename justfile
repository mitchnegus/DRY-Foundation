package_dir := "src/dry_foundation"
docs_dir := "docs"
docs_src := docs_dir / "source"
docs_html := docs_dir / "build/html"


[private]
@check-uv:
    command -v uv >/dev/null || (echo "Error: 'uv' is not installed.")


[private]
@clean-docs:
    rm -rf {{ docs_src }}/api


[doc("Build documentation")]
@docs: check-uv clean-docs
    uv run --group docs sphinx-apidoc -f -o {{ docs_src }}/api {{ package_dir }}
    uv run --group docs sphinx-build -b html {{ docs_src }} {{ docs_html }}


[doc("Run a quick set of tests")]
@test-quick: check-uv
    uv run pytest tests/


[doc("Run tests")]
@test: check-uv
    uvx nox -s test


[doc("Format the package source code")]
@format: check-uv
    echo "Format imports:"
    uvx ruff check --select I --fix
    echo "Format source:"
    uvx ruff format


[doc("Check source code formatting")]
[arg("flag", pattern="--help|--check|--diff")]
@format-check flag="--check": check-uv
    echo "Check import sorting:"
    uvx ruff check --select I {{ if flag == "--check" { "" } else { flag } }}
    echo "Check source code formatting:"
    uvx ruff format {{ flag }}


[doc("Lint the package source code")]
@lint *flags: check-uv
    echo "Lint source code:"
    uvx ruff check {{ flags }}


[doc("Bundle the package for distribution")]
@package: check-uv
    uv build --no-sources


[doc("Publish the package to PyPI")]
@publish: check-uv
    uv publish --username __token__ --password $(cat .TOKEN)


[doc("Clean all automatically generated files")]
@clean: clean-docs
	rm -rf {{ package_dir }}/_version.py
	rm -rf htmlcov/
	rm -rf dist/ *egg-info/
	rm -rf .pytest_cache/
	rm -rf .venv
	rm -rf .nox
