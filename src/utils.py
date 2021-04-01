from typing import Callable
import importlib
import logging

LOG = logging.getLogger(__name__)


def get_function_from_string(function_path: str) -> Callable:
    """
    Get the actual function from the module path string
    """
    module_path = ".".join(function_path.split(".")[:-1])
    func_name = function_path.split(".")[-1]
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        return None
    else:
        return getattr(module, func_name, None)


def request_to_event(
    path: str, method: str, qs: dict, body: str, headers: dict
) -> dict:
    """
    Convert Flask request to lambda API GW request
    """
    event = {
        "body": body,
        "resource": "/{proxy+}",
        "path": path,
        "httpMethod": method,
        "isBase64Encoded": False,
        "headers": headers,
        "queryStringParameters": qs,
    }
    LOG.debug(event)
    return event
