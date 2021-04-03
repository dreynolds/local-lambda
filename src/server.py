from collections import OrderedDict
from http.server import HTTPServer, BaseHTTPRequestHandler
from http import HTTPStatus
import logging
import json
import os
import subprocess
from urllib.parse import urlparse, parse_qs

from utils import request_to_event

LOG = logging.getLogger(__name__)


class LambdaHandler(BaseHTTPRequestHandler):

    def _bad_method_response(self):
        return {
            "body": "Bad method",
            "statusCode": HTTPStatus.METHOD_NOT_ALLOWED.value,
        }

    def _call_method(self, path, method, qs, body, headers):
        function_details = server_methods.get(path, {}).get(method, {})
        function_path = function_details.get("function", None)
        function_env = function_details.get("env", {})
        current_env = os.environ.copy()
        current_env.update(function_env)
        LOG.debug("Generated ENV: %s", current_env)

        if function_path is not None:
            event = request_to_event(path, method, qs, body, headers)
            output = subprocess.check_output(
                ["call_command.py", function_path, "--event", json.dumps(event)],
                env=current_env,
            )
            try:
                output = json.loads(output)
            except json.JSONDecodeError:
                output = self._bad_method_response()
                LOG.exception("Error decoding method output: %s", output)
            else:
                LOG.debug("Command output: %s", output)
            return output
        return self._bad_method_response()
    def _process(self, method):
        url = urlparse(self.path)
        qs = parse_qs(url.query)
        response = self._call_method(
            url.path,
            method,
            qs,
            "",
            self.headers.__dict__,
        )
        self.send_response(response["statusCode"])
        for header, value in response.get("headers", {}).items():
            self.send_header(header, value)
        self.end_headers()
        self.wfile.write(response["body"].encode("utf-8"))

    def do_GET(self):
        self._process("GET")

    def do_POST(self):
        self._process("POST")

    def do_HEAD(self):
        self._process("HEAD")

    def do_OPTIONS(self):
        self._process("OPTIONS")


def run(address="localhost", port=5000):
    LOG.info("lambda_server starting up on %s:%s", address, port)
    httpd = HTTPServer((address, port), LambdaHandler)
    httpd.serve_forever()


class AlreadyRegistered(Exception):
    pass


class MethodRegistry(OrderedDict):
    def register(self, url, method_map):
        if url in self:
            msg = "This URL is already registered"
            raise AlreadyRegistered(msg)
        self[url] = method_map


server_methods = MethodRegistry()
