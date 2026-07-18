"""Objects for handling API request responses."""

from functools import wraps

from flask import jsonify


def fetch_json_envelope(view_func):
    """
    Wrap a Flask route so that raw HTML responses are returned as JSON.

    This lets client-side ``fetch`` calls always expect
    ``Content-Type: application/json``, while still being able to render
    HTML fragments. Routes wrapped with this decorator must only return
    a string with HTML content, or a tuple where the first element of
    the tuple is a string with HTML content.

    For example, given a view returning HTML content, the response is:

        ``{ "type": "html", "content": "<div>...</div>" }``

    """

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        response = view_func(*args, **kwargs)
        if isinstance(response, tuple):
            body, status, headers = _unpack_response(*response)
        else:
            body, status, headers = response, 200, None
        return jsonify({"type": "html", "content": body}), status, headers

    return wrapper


def _unpack_response(body=None, status=200, headers=None):
    if not isinstance(body, str):
        raise TypeError(
            f"Could not unpack response given body of type `{type(body)}`; "
            "the view function in question must return a string as the first value."
        )
    # Flask allows headers to be the second argument in 2-element tuples
    if headers is None and not isinstance(status, (int, str)):
        status, headers = 200, status
    return body, status, headers
