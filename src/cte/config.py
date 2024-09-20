import tomllib
from typing import Tuple


def get_config_entries(config_path: str) -> Tuple[str, str, str]:
    with open(config_path, 'rb') as stream:
        config = tomllib.load(stream)

    fields = ['confluence-url', 'confluence-rest-url', 'personal-access-token']
    url_fields = {fields[0], fields[1]}
    for field in fields:
        if field not in config:
            raise RuntimeError(f'The config does not specify the "{field}" field')
        value = config[field]
        if not isinstance(value, str):
            raise RuntimeError(f'The field value of "{field}" is not a string')
        if field in url_fields:
            if value[-1] != '/':
                config[field] = f'{value}/'

    return tuple(config[field] for field in fields)
