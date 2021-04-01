import argparse
import logging
import os
import sys

from config import UrlConfigFile
from server import run, server_methods, AlreadyRegistered

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


def main() -> None:
    parser = argparse.ArgumentParser(description="LambdaLocal")
    parser.add_argument(
        "--port",
        dest="server_port",
        action="store",
        help="The port to run the API on",
        default=os.environ.get("PORT", DEFAULT_PORT),
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

    for url, method_config in config.get("endpoints", {}).items():
        try:
            server_methods.register(url.upper(), method_config)
        except AlreadyRegistered:
            LOG.debug("%s already registered, ignoring", url)

    run(port=args.server_port)
