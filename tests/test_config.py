from pathlib import Path
from unittest.mock import patch, DEFAULT

import pytest

from config import UrlConfigFile


@pytest.mark.parametrize("exists,is_file,expected", [
    (False, False, None),
    (True, False, None),
    (False, True, None),
    (True, True, Path),
])
def test_load_file(exists, is_file, expected):
    c = UrlConfigFile(file_name='./config')

    with patch.multiple('config.Path', exists=DEFAULT, is_file=DEFAULT) as mocks:
        mocks['exists'].return_value = exists
        mocks['is_file'].return_value = is_file
        f = c.load_file(c.file_name)
        if expected is None:
            assert f is None
        else:
            assert isinstance(f, expected)


def test_get_config():
    c = UrlConfigFile(file_name='./config')

    with patch.object(UrlConfigFile, 'load_file') as mock_load_file:
        mock_load_file.return_value = Path('./tests/data/config.json')
        with patch.object(UrlConfigFile, 'validate_config') as mock_validate_config:
            c.get_config()

            assert mock_load_file.called
            assert mock_validate_config.called
