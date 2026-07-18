package_dir := "src/dry_foundation"
docs_dir := "docs"
docs_src := docs_dir / "source"
docs_html := docs_dir / "build/html"


[private]
@check-uv:
    command -v uv > /dev/null || (echo "Error: 'uv' is not installed.")


[private]
@check-npm:
    command -v npm > /dev/null || (echo "Error: 'npm' is not installed.")


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


[doc("Format the Python package source code")]
@format-python: check-uv
    echo "Format Python imports:"
    uvx ruff check --select I --fix
    echo "Format Python source:"
    uvx ruff format

[doc("Format the JavaScript package source code")]
@format-js: check-npm
    echo "Format Javascript:"
    npx prettier --write .


[doc("Format the package source code")]
@format: format-python format-js


[doc("Check source code formatting")]
[arg("flag", pattern="--help|--check|--diff")]
@format-check flag="--check": check-uv
    echo "Check Python import sorting:"
    uvx ruff check --select I {{ if flag == "--check" { "" } else { flag } }}
    echo "Check Python source code formatting:"
    uvx ruff format {{ flag }}
    echo "Check JavaScript source code formatting:"
    npx prettier --check .


[doc("Lint the Python package source code")]
@lint-python *flags: check-uv
    echo "Lint Python source code:"
    uvx ruff check {{ flags }}


[doc("Lint the JavaScript package source code")]
@lint-js: check-npm
    echo "Lint JavaScript source code:"
    npm run lint


[doc("Lint the package source code")]
@lint: lint-python lint-js


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
