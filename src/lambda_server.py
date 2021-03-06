import argparse
import importlib
import logging
import os
import sys
from typing import Callable

from flask import Flask, Response, request

from config import UrlConfigFile

app = Flask(__name__)
LOG = logging.getLogger(__name__)
DEFAULT_PORT = 5000


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


def convert_response(resp: dict):
    """
    Convert API GW style lambda response to Flask response
    """
    response = Response(
        resp.get('body', ''),
        status=resp.get('statusCode', 200),
    )
    response.headers.update(resp.get('headers', {}))
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
    if format is None:
        format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(
        level=level,
        format=format,
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
        dest="debugging",
        action="store_true",
        help="debug logging?"
    )
    args = parser.parse_args()

    configure_logging(args.debugging)

    config = UrlConfigFile(file_name=args.config_path).get_config()
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
    app.run(
        port=args.flask_port,
        debug=args.debugging,
    )
