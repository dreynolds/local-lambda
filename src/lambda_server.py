import argparse
import importlib
import json
import logging
import os
import sys
from typing import Callable
from pathlib import Path

from flask import Flask, Response, request

app = Flask(__name__)
LOG = logging.getLogger(__name__)
DEFAULT_PORT = 5000


def get_config(path: str) -> dict:
    config_file = Path(path)
    if not config_file.exists() or not config_file.is_file():
        LOG.debug(f'"{config_file}" does not exist')
        return None

    try:
        config_data = json.load(config_file.open())
    except json.decoder.JSONDecodeError:
        LOG.debug(f'"{config_file}" is not readable JSON')
        return None

    # FIXME: check for keys we'll need
    return config_data


def get_function_from_string(function_path: str) -> Callable:
    """
    Get the actual function from the module path string
    """
    module_path = '.'.join(function_path.split('.')[:-1])
    func_name = function_path.split('.')[-1]
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        return None
    else:
        return getattr(module, func_name, None)


def request_to_event(request) -> dict:
    """
    Convert Flask request to lambda API GW request
    """
    event = {
        'body': request.get_data(),
        "resource": "/{proxy+}",
        "path": request.path,
        "httpMethod": request.method,
        "isBase64Encoded": False,
        "headers": {}
    }
    for k, v in request.headers.items():
        event['headers'][k] = v
    LOG.debug(event)
    return event


def convert_response(resp):
    """
    Convert API GW style lambda response to Flask response
    """
    response = Response(
        resp.get('body'),
        status=resp.get('statusCode', 200),
    )
    response.headers.update(resp.get('headers'))
    return response


def default_method(config: dict) -> Callable:
    """
    Method to use for calling lambda function cod
    """
    def inner_method():
        function_path = config.get(request.method, {}).get('function', None)
        func = get_function_from_string(function_path)
        if func is not None:
            event = request_to_event(request)
            response = func(event, {})
            return convert_response(response)
        return Response("Bad method", status=405)
    return inner_method


def configure_logging(debug: str, format=None) -> None:
    # FIXME: formatter
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(
        level=level,
    )

def main() -> None:
    parser = argparse.ArgumentParser(description="LambdaLocal")
    parser.add_argument(
        '--port',
        dest='flask_port',
        action='store',
        help="The port to run the API on",
        default=os.environ.get('PORT', DEFAULT_PORT),
    )
    parser.add_argument(
        '-c',
        '--config',
        dest='config_path',
        action='store',
        help="The path to the config file",
        default="./.local-lambda.json",
    )
    parser.add_argument(
        '--debug',
        dest="debug_log",
        action="store_true",
        help="debug logging?"
    )
    args = parser.parse_args()

    configure_logging(args.debug_log)

    config = get_config(args.config_path)
    if not config:
        sys.exit("Config file not found or unparseable")

    for url, method_config in config.get('endpoints', {}).items():
        method_suffix = url.replace('/', '')
        extra_config = {
            'methods': method_config.keys(),
        }

        app.add_url_rule(
            url,
            f'default_method_{method_suffix}',
            default_method(method_config),
            **extra_config,
        )
    app.run(port=args.flask_port)
