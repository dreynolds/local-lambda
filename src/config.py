import json
import logging
from pathlib import Path
from typing import Union

import jsonschema  # type: ignore

from config_schema import CONFIG_SCHEMA

LOG = logging.getLogger(__name__)


class UrlConfigFile:
    def __init__(self, *args, **kwargs):
        self.file_name = kwargs.pop("file_name")
        self.schema = kwargs.pop("schema", CONFIG_SCHEMA)

    def load_file(self, file_name: str) -> Union[Path, None]:
        config_file = Path(file_name)
        if not config_file.exists() or not config_file.is_file():
            LOG.debug(f'"{self.file_name}" does not exist')
            return None
        return config_file

    def validate_config(self, config_data: str) -> Union[str, None]:
        # Validate config schema
        try:
            jsonschema.validate(instance=config_data, schema=CONFIG_SCHEMA)
        except jsonschema.exceptions.ValidationError:
            LOG.debug(f'"{self.file_name}" is in a bad format')
            return None
        else:
            return config_data

    def get_config(self) -> Union[dict, None]:
        config_file = self.load_file(self.file_name)
        try:
            config_data = json.load(config_file.open())
            LOG.debug(config_data)
        except json.decoder.JSONDecodeError:
            LOG.debug(f'"{self.file_name}" is not readable JSON')
            return None
        return self.validate_config(config_data)
