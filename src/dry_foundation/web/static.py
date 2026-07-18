"""Share static assets with applications built on DRY Foundation."""

import json

from flask import Blueprint, url_for

# Define the blueprint
static_assets_blueprint = Blueprint(
    "dry_foundation",
    __name__,
    static_folder="static",
    static_url_path="/dry-foundation/static",
)

JS_MODULES = {
    "dry-foundation/requests": "js/modules/requests.js",
    "dry-foundation/form-suggestions": "js/modules/form-suggestions.js",
    "dry-foundation/autocomplete-input": "js/modules/autocomplete-input.js",
}


def build_javascript_import_map():
    """Build an import map for JavaScript modules bundled with this package."""
    imports = {
        specifier: url_for("dry_foundation.static", filename=filename)
        for specifier, filename in JS_MODULES.items()
    }
    return json.dumps({"imports": imports})
