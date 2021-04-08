import argparse
import logging
import os
import sys

from config import UrlConfigFile
from server import AlreadyRegistered, run, server_methods

LOG = logging.getLogger(__name__)
DEFAULT_PORT = 5000


def configure_logging(debug: str, format=None) -> None:
    if format is None:
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(
        level=level,
        format=format,
    )


def register_methods(config):
    for url, method_config in config.get("endpoints", {}).items():
        method_config = {k.upper(): v for k, v in method_config.items()}
        try:
            server_methods.register(url, method_config)
        except AlreadyRegistered:
            LOG.debug("%s already registered, ignoring", url)


def main() -> None:
    parser = argparse.ArgumentParser(description="LambdaLocal")
    parser.add_argument(
        "--port",
        dest="server_port",
        action="store",
        help="The port to run the API on",
        default=os.environ.get("PORT", DEFAULT_PORT),
        type=int,
    )
    parser.add_argument(
        "-c",
        "--config",
        dest="config_path",
        action="store",
        help="The path to the config file",
        default="./.local-lambda.json",
    )
    parser.add_argument(
        "--debug", dest="debugging", action="store_true", help="debug logging?"
    )
    args = parser.parse_args()

    configure_logging(args.debugging)

    config = UrlConfigFile(file_name=args.config_path).get_config()
    if not config:
        sys.exit("Config file not found or unparseable")

    register_methods(config)
    run(port=args.server_port)
