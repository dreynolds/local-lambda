from unittest import mock

from utils import request_to_event
from lambda_server import register_methods


def test_request_to_event():
    path = "/"
    method = "POST"
    qs = {}
    body = "BODY"
    headers = {"_headers": [("Host", "example.org"), ("Connection", "keep-alive")]}
    event = request_to_event(path, method, qs, body, headers)
    assert event == {
        "body": body,
        "resource": "/{proxy+}",
        "path": path,
        "httpMethod": method,
        "isBase64Encoded": False,
        "headers": {
            "Host": "example.org",
            "Connection": "keep-alive",
        },
        "queryStringParameters": qs,
    }


def test_register_methods():
    """
    Methods should be upper cased for consistency
    """
    URL = "/"
    METHOD_CONFIG = {"post": {"function": "thing"}, "geT": {"function": "thing"}}

    config = {"endpoints": {URL: METHOD_CONFIG}}

    with mock.patch("lambda_server.server_methods.register") as mock_register:
        register_methods(config)

        mock_register.assert_called_once_with(
            URL, {k.upper(): v for k, v in METHOD_CONFIG.items()}
        )
