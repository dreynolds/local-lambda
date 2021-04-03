from collections import OrderedDict
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
from urllib.parse import urlparse, parse_qs

from utils import get_function_from_string, request_to_event

LOG = logging.getLogger(__name__)


class LambdaHandler(BaseHTTPRequestHandler):
    def _call_method(self, path, method, qs, body, headers):
        function_path = (
            server_methods.get(path, {}).get(method, {}).get("function", None)
        )
        if function_path is not None:
            func = get_function_from_string(function_path)
            if func is not None:
                event = request_to_event(path, method, qs, body, headers)
                return func(event, {})
        return {
            "body": "Bad method",
            "statusCode": 405,
        }

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
