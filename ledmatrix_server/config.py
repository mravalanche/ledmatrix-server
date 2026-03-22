import os

from dotenv import load_dotenv
from dataclasses import dataclass, fields

from ledmatrix_server.common import log

@dataclass(frozen=True)
class Config:
    hass_key: str
    hass_url: str
    output_path: str


load_dotenv()

def get_env(key:str) -> str:
    value:str|None = os.environ.get(key)
    if not value:
        log.debug(f"Unable to find {key} in environmental variables")
        raise RuntimeError(f"{key} not found")
    
    value_str = str(value)
    log.info(f"Found env: {key} ({len(value_str)} chars)")
    return value_str


def load_config() -> Config:
    values = {
        f.name: get_env(f.name.upper())
        for f in fields(Config)
    }
    return Config(**values)

config = load_config()
